#include <stdio.h>

#include "nodePath.h"

#include "ik/ik.h"
#include "kphys/core/panda/armature.h"
#include "kphys/core/panda/bone.h"
#include "kphys/core/panda/converters.h"
#include "kphys/core/panda/ik.h"
#include "kphys/core/panda/types.h"


TypeHandle BoneNode::_type_handle;

BoneNode::BoneNode(const char* name, unsigned int bone_id):
    PandaNode(name),
    _bone_id(bone_id),
    _axis(LVector3::zero()),
    _min_ang(-M_PI),
    _max_ang(M_PI),
    _is_static(false),
    _ik_node(NULL) {}

unsigned int BoneNode::get_bone_id() {
    return _bone_id;
}

/**
 * Set hinge constraint.
 * [CCDIK]
 */
void BoneNode::set_hinge_constraint(const LVecBase3& axis, double min_ang, double max_ang) {
    _axis = axis;
    _min_ang = min_ang;
    _max_ang = max_ang;
}

/**
 * Set ball constraint.
 * [CCDIK]
 */
void BoneNode::set_ball_constraint(double min_ang, double max_ang) {
    _axis = -1;
    _min_ang = min_ang;
    _max_ang = max_ang;
}

/**
 * Check if bone is static and not affected by IK.
 * [CCDIK]
 */
bool BoneNode::is_static() {
    return _is_static;
}

/**
 * Set/unset static flag. Static bones are not affected by IK.
 * [CCDIK]
 */
void BoneNode::set_static(bool is_static) {
    _is_static = is_static;
}

/**
 * Get constraint axis. Returns zero-length vector for hidge constraints.
 * [CCDIK]
 */
LVector3 BoneNode::get_axis() {
    return _axis;
}

/**
 * Get constraint min angle.
 * [CCDIK]
 */
double BoneNode::get_min_angle() {
    return _min_ang;
}

/**
 * Get constraint min angle.
 * [CCDIK]
 */
double BoneNode::get_max_angle() {
    return _max_ang;
}

/**
 * Get IK node. Returns a reference to an external library's structure.
 * [IK]
 */
struct ik_node_t* BoneNode::get_ik_node() {
    return _ik_node;
}

/**
 * Rebuilds external library's structures.
 * [IK]
 */
unsigned int BoneNode::rebuild_ik_recursive(struct ik_solver_t* ik_solver, unsigned int node_id) {
    NodePath bone = NodePath::any_path(this);
    NodePath parent_bone = bone.get_parent();

    if (is_armature(parent_bone)) {
        _ik_node = ik_solver->node->create(node_id);
        node_id++;

    } else if (is_bone(parent_bone)) {
        // parent is bone, so this bone becomes child bone
        _ik_node = ik_solver->node->create_child(
            ((BoneNode*) parent_bone.node())->get_ik_node(), node_id);
        node_id++;
    }

    node_id = children_rebuild_ik(bone, ik_solver, node_id);
    return node_id;
}

void BoneNode::sync_p2ik_recursive() {
    NodePath bone = NodePath::any_path(this);

    if (_ik_node != NULL) {
        _ik_node->position = LVecBase3_to_IKVec3(bone.get_pos());
        _ik_node->rotation = LQuaternion_to_IKQuat(bone.get_quat());
    }

    children_sync_p2ik(bone);
}

void BoneNode::sync_ik2p_local() {
    NodePath bone = NodePath::any_path(this);

    if (_ik_node != NULL) {
        // bone.set_pos(IKVec3_to_LVecBase3(_ik_node->position));
        bone.set_quat(IKQuat_to_LQuaternion(_ik_node->rotation));
    }
}
