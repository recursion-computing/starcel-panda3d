#include <stdio.h>
#include <string.h>

#include "kphys/core/panda/armature.h"
#include "kphys/core/panda/bone.h"
#include "kphys/core/panda/effector.h"
#include "kphys/core/panda/ik.h"
#include "kphys/core/panda/types.h"


TypeHandle ArmatureNode::_type_handle;

ArmatureNode::ArmatureNode(const char* name):
        PandaNode(name),
        _ik_engine(-1),
        _ik_solver(NULL) {

    _bone_init_local = (LMatrix4Array*) malloc(sizeof(LMatrix4Array));
    _bone_init_inv = (LMatrix4Array*) malloc(sizeof(LMatrix4Array));
    _bone_transform = (LMatrix4Array*) malloc(sizeof(LMatrix4Array));

    _bone_transform_tex = new Texture();
    _bone_transform_tex->setup_buffer_texture(
        RGBA_MAT4_SIZE * MAX_BONES, Texture::T_float,
        Texture::F_rgba32, GeomEnums::UH_static);

    _bone_prev_transform_tex = new Texture();
    _bone_prev_transform_tex->setup_buffer_texture(
        RGBA_MAT4_SIZE * MAX_BONES, Texture::T_float,
        Texture::F_rgba32, GeomEnums::UH_static);

    for (unsigned int i = 0; i < MAX_BONES; i++)
        _frame_transform_indices[i] = -1;
}

ArmatureNode::~ArmatureNode() {
    if (_ik_solver != NULL)
        ik.solver.destroy(_ik_solver);
    _bones.clear();

    free(_bone_init_local);
    free(_bone_init_inv);
    free(_bone_transform);
}

void ArmatureNode::cleanup() {
    NodePath armature = NodePath::any_path(this);
    armature.clear_shader_input("bone_transform_tex");
    armature.clear_shader_input("bone_prev_transform_tex");
}

void ArmatureNode::reset() {
    NodePath armature = NodePath::any_path(this);
    NodePathCollection effectors = armature.find_all_matches("**/+EffectorNode");
    NodePathCollection bones = armature.find_all_matches("**/+BoneNode");

    // save effectors
    for (int i = 0; i < effectors.get_num_paths(); i++) {
        NodePath np = effectors.get_path(i);
        ((EffectorNode*) np.node())->sync_p2ik_local();
    }

    // reset bones
    for (int i = 0; i < bones.get_num_paths(); i++) {
        NodePath np = bones.get_path(i);
        unsigned int bone_id = ((BoneNode*) np.node())->get_bone_id();
        np.set_mat(get_matrix(_bone_init_local, bone_id));
    }

    // restore effectors
    for (int i = 0; i < effectors.get_num_paths(); i++) {
        NodePath np = effectors.get_path(i);
        ((EffectorNode*) np.node())->sync_ik2p_local();
    }
}

void ArmatureNode::rebuild_bind_pose() {
    NodePath armature = NodePath::any_path(this);
    _update_matrices(armature, LMatrix4::ident_mat(), 0);
}

void ArmatureNode::rebuild_ik(unsigned int ik_engine) {
    _ik_engine = ik_engine;

    if (_ik_engine == IK_ENGINE_IK) {
        if (_ik_solver != NULL)
            ik.solver.destroy(_ik_solver);
        _ik_solver = ik.solver.create(IK_FABRIK);
        _ik_solver->flags &= ~IK_ENABLE_CONSTRAINTS;
        _ik_solver->flags &= ~IK_ENABLE_TARGET_ROTATIONS;
        _ik_solver->flags |= IK_ENABLE_JOINT_ROTATIONS;
        _ik_solver->max_iterations = 5;

        NodePath armature = NodePath::any_path(this);
        children_rebuild_ik(armature, _ik_solver, 0);
    }
}

/**
 * Update IK for the all effectors.
 */
void ArmatureNode::update_ik() {
    NodePath armature = NodePath::any_path(this);

    unsigned int priority = 0, max_priority = 0;
    NodePathCollection nps = armature.find_all_matches("**/+EffectorNode");
    for (int i = 0; i < nps.get_num_paths(); i++) {
        NodePath np = nps.get_path(i);
        priority = ((EffectorNode*) np.node())->get_priority();
        if (priority > max_priority)
            max_priority = priority;
    }

    for (int priority = 0; priority <= max_priority; priority++)
        update_ik(priority);
}

/**
 * Update IK for the effectors with specified priority.
 */
void ArmatureNode::update_ik(unsigned int priority) {
    for (int i = 0; i < 10; i++) {
        sync_p2ik_recursive();  // write all bones
        solve_ik(priority);  // solve IK problem
        sync_ik2p_chains();  // read bones from active chains
    }
}

/**
 * Update shader inputs with world space bone matrices.
 */
void ArmatureNode::update_shader_inputs() {
    NodePath armature = NodePath::any_path(this);

    PTA_uchar data = _bone_prev_transform_tex->modify_ram_image();
    memcpy(data.p(), _bone_transform->data, sizeof(_bone_transform->data));
    armature.set_shader_input("bone_prev_transform_tex", _bone_prev_transform_tex);

    _update_matrices(armature, LMatrix4::ident_mat(), 1);

    data = _bone_transform_tex->modify_ram_image();
    memcpy(data.p(), _bone_transform->data, sizeof(_bone_transform->data));
    armature.set_shader_input("bone_transform_tex", _bone_transform_tex);
}

/**
 * Fill bone matrices array with world-space bone matrices
 * by recursively walking through the node graph.
 */
void ArmatureNode::_update_matrices(NodePath np, LMatrix4 parent_mat, bool is_current) {
    LMatrix4 mat = LMatrix4::ident_mat();

    if (is_bone(np)) {
        unsigned int bone_id = ((BoneNode*) np.node())->get_bone_id();
        mat = np.get_mat() * parent_mat;  // get world-space matrix

        if (is_current) {  // current matrices
            // https://github.com/KhronosGroup/glTF-Tutorials/blob/master/gltfTutorial/gltfTutorial_020_Skins.md#the-joint-matrices
            set_matrix(_bone_transform, bone_id, get_matrix(_bone_init_inv, bone_id) * mat);

        } else {  // initial matrices
            set_matrix(_bone_init_local, bone_id, np.get_mat());
            LMatrix4 inv_mat;
            inv_mat.invert_from(mat);
            set_matrix(_bone_init_inv, bone_id, inv_mat);
        }
    }

    for (int i = 0; i < np.get_num_children(); i++) {
        NodePath child_np = np.get_child(i);
        if (is_bone(child_np))
            _update_matrices(child_np, mat, is_current);
    }
}

/**
 * Solve Inverse Kinematics problem.
 */
void ArmatureNode::solve_ik(unsigned int priority) {
    NodePath armature = NodePath::any_path(this);
    NodePath root_bone = NodePath::not_found();
    for (int i = 0; i < armature.get_num_children(); i++) {
        NodePath child = armature.get_child(i);
        if (is_bone(child)) {
            root_bone = child;
            break;
        }
    }

    if (!root_bone)
        return;

    NodePathCollection nps = armature.find_all_matches("**/+EffectorNode");
    for (int i = 0; i < nps.get_num_paths(); i++) {
        NodePath np = nps.get_path(i);
        if (((EffectorNode*) np.node())->get_priority() == priority)
            ((EffectorNode*) np.node())->set_weight(1);
        else
            ((EffectorNode*) np.node())->set_weight(0);
    }

    switch (_ik_engine) {
    case IK_ENGINE_IK:
        ik.solver.set_tree(_ik_solver, ((BoneNode*) root_bone.node())->get_ik_node());
        ik.solver.rebuild(_ik_solver);
        ik.solver.solve(_ik_solver);
        ik.solver.unlink_tree(_ik_solver);
        break;

    case IK_ENGINE_CCDIK:
        for (int i = 0; i < nps.get_num_paths(); i++) {
            NodePath np = nps.get_path(i);
            EffectorNode* effector = (EffectorNode*) np.node();
            if (effector->get_weight())
                effector->inverse_kinematics_ccd();
        }
        break;

    default:
        break;
    }
}

/**
 * Recursively sync all Panda3D nodes to IK nodes and effectors.
 */
void ArmatureNode::sync_p2ik_recursive() {
    NodePath armature = NodePath::any_path(this);
    children_sync_p2ik(armature);
}

/**
 * Sync IK effector affected chains to Panda3D related nodes.
 */
void ArmatureNode::sync_ik2p_chains() {
    NodePath armature = NodePath::any_path(this);
    NodePathCollection nps = armature.find_all_matches("**/+EffectorNode");
    for (int i = 0; i < nps.get_num_paths(); i++) {
        NodePath np = nps.get_path(i);
        ((EffectorNode*) np.node())->sync_ik2p_chain_reverse();
    }
}


NodePath ArmatureNode::find_bone(const char* name) {
    std::string s = std::string(name);
    if (_bones.find(s) != _bones.end())
        return _bones[s];

    NodePath armature = NodePath::any_path(this);
    NodePathCollection bones = armature.find_all_matches("**/+BoneNode");
    for (int i = 0; i < bones.get_num_paths(); i++) {
        NodePath np = bones.get_path(i);
        if (strcmp(np.get_name().c_str(), name) == 0) {
            _bones[s] = np;
            return np;
        }
    }

    _bones[s] = NodePath();
    return _bones[s];
}

/**
 * Set animation frame. Modifies bone transforms.
 */
void ArmatureNode::apply(PointerTo<Frame> frame) {
    NodePath armature = NodePath::any_path(this);

    unsigned int nt = frame->get_num_transforms();
    for (unsigned int i = 0; i < nt; i++) {
        const char* name  = frame->get_bone_name(i);
        NodePath np = find_bone(name);
        if (np.is_empty())
            continue;

        ConstPointerTo<TransformState> transform = frame->get_transform(name);
        if (transform == NULL)
            continue;

        unsigned short flags = frame->get_transform_flags(name);
        if (flags & TRANSFORM_POS)
            np.set_pos(transform->get_pos());
        if (flags & TRANSFORM_HPR)
            np.set_hpr(transform->get_hpr());
        if (flags & TRANSFORM_QUAT)
            np.set_quat(transform->get_quat());
    }
}
