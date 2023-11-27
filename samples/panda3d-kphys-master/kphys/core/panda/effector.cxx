/* https://docs.microsoft.com/en-us/cpp/c-runtime-library/math-constants?view=msvc-170 */
#define _USE_MATH_DEFINES // for C
#include <math.h>

#include <stdio.h>

#include "nodePath.h"

#include "kphys/core/panda/bone.h"
#include "kphys/core/panda/ccdik.h"
#include "kphys/core/panda/converters.h"
#include "kphys/core/panda/effector.h"
#include "kphys/core/panda/ik.h"
#include "kphys/core/panda/types.h"


TypeHandle EffectorNode::_type_handle;

EffectorNode::EffectorNode(
        const char* name, unsigned int chain_length, unsigned int priority):
    PandaNode(name),
    _chain_length(chain_length),
    _priority(priority),
    _ik_effector(NULL) {}

unsigned int EffectorNode::get_chain_length() {
    return _chain_length;
}

NodePath EffectorNode::get_chain_root() {
    NodePath effector = NodePath::any_path(this);
    NodePath chain_root = effector;
    for (int i = 0; i < _chain_length + 2; i++)
        chain_root = chain_root.get_parent();
    return chain_root;
}

unsigned int EffectorNode::get_priority() {
    return _priority;
}

double EffectorNode::get_weight() {
    return _weight;
}

void EffectorNode::set_weight(double weight) {
    _weight = weight;
    if (_ik_effector != NULL)
        _ik_effector->weight = weight;
}

/**
 * Get IK effector. Returns a reference to an external library's structure.
 * [IK]
 */
struct ik_effector_t* EffectorNode::get_ik_effector() {
    return _ik_effector;
}

/**
 * Rebuilds external library's structures.
 * [IK]
 */
unsigned int EffectorNode::rebuild_ik(struct ik_solver_t* ik_solver, unsigned int node_id) {
    NodePath effector = NodePath::any_path(this);
    NodePath parent_bone = effector.get_parent();

    if (is_bone(parent_bone)) {
        _ik_effector = ik_solver->effector->create();
        ik_solver->effector->attach(
            _ik_effector,
            ((BoneNode*) parent_bone.node())->get_ik_node());

        _ik_effector->chain_length = _chain_length;
        _ik_effector->weight = _weight;
    }

    return node_id;
}

void EffectorNode::sync_p2ik_local() {
    NodePath effector = NodePath::any_path(this);
    NodePath armature = get_armature(effector);
    NodePath chain_root = get_chain_root();

    // IK positions and rotations are relative to chain root
    if (_ik_effector != NULL) {
        _ik_effector->target_position = LVecBase3_to_IKVec3(effector.get_pos(chain_root));
        _ik_effector->target_rotation = LQuaternion_to_IKQuat(effector.get_quat(chain_root));
    }

    // save world-space position and rotation
    _position = effector.get_pos(armature);
    // _rotation = effector.get_quat(armature);
}

void EffectorNode::sync_ik2p_local() {
    NodePath effector = NodePath::any_path(this);
    NodePath armature = get_armature(effector);

    // restore world-space position and rotation
    effector.set_pos(armature, _position);
    effector.set_quat(armature, LQuaternion::ident_quat());
}

/**
 * Sync IK effector affected chain starting from IK effector.
 */
void EffectorNode::sync_ik2p_chain_reverse() {
    NodePath effector = NodePath::any_path(this);
    NodePath armature = get_armature(effector);

    if (get_weight()) {
        // set chain starting from effector
        NodePath chain[256];
        NodePath chain_root = effector;
        for (int i = 0; i < _chain_length + 2; i++) {
            chain_root = chain_root.get_parent();
            chain[i] = chain_root;
        }

        // update chain starting from chain root
        for (int i = _chain_length; i >= 0; i--)
            ((BoneNode*) chain[i].node())->sync_ik2p_local();
    }

    // update myself
    sync_ik2p_local();
}

void EffectorNode::inverse_kinematics_ccd(
        double threshold, unsigned int min_iterations, unsigned int max_iterations) {
    NodePath target = NodePath::any_path(this);
    NodePath end_effector = target.get_parent();
    NodePath armature = get_armature(target);

    // save world-space target position because it will be modified
    sync_p2ik_local();
    LPoint3 target_pos_ws = target.get_pos(armature);

    double err, ang;
    bool target_reached = false;
    for (unsigned int i = 0; i < max_iterations; i++) {
        if (i >= min_iterations) {
            err = (target_pos_ws - end_effector.get_pos(armature)).length();
            if (err < threshold) {
                target_reached = true;
                break;
            }
        }

        NodePath bone = target;
        for (unsigned int j = 0; j < _chain_length + 1; j++) {
            bone = bone.get_parent();

            if (((BoneNode*) bone.node())->is_static())
                continue;

            // same as "target.get_pos(bone)" but using saved world-space position
            LPoint3 target_pos = bone.get_relative_point(armature, target_pos_ws);

            LPoint3 pos = LPoint3::zero();
            LPoint3 ee = end_effector.get_pos(bone);

            LVector3 d1 = target_pos - pos;
            LVector3 d2 = ee - pos;

            LVector3 cross = d1.cross(d2).normalized();
            if (cross.length_squared() < 1e-9)
                continue;

            ang = d2.normalized().signed_angle_rad(d1.normalized(), cross);
            LQuaternion q;
            q.set_from_axis_angle_rad(ang, cross);
            // Add this rotation to the current rotation:
            LQuaternion q_old = bone.get_quat(armature);
            LQuaternion q_new = q * q_old;
            q_new.normalize();

            // Correct rotation for hinge:
            LVector3 axis = ((BoneNode*) bone.node())->get_axis();
            if (axis != LVector3::zero()) {
                LVector3 my_axis_in_parent_space = axis;
                LMatrix4 swing_twist = swing_twist_decomposition(q_new, -my_axis_in_parent_space);
                LQuaternion swing = (LQuaternion) swing_twist.get_row(0);
                LQuaternion twist = (LQuaternion) swing_twist.get_row(1);
                q_new = twist;
            }

            LVector3 rot_axis = q_new.get_axis();
            rot_axis.normalize();
            ang = q_new.get_angle_rad();
            if (rot_axis.length_squared() > 1e-3 && !isnan(ang) && fabs(ang) > 0) {  // valid rotation axis?
                // reduce the angle
                ang = fmod(ang, (M_PI * 2));
                // force into the minimum absolute value residue class, so that -180 < angle <= 180
                if (ang > M_PI)
                    ang -= 2 * M_PI;

                if (fabs(ang) > 1e-6 && fabs(ang) < M_PI * 2) {
                    double min_ang = ((BoneNode*) bone.node())->get_min_angle();
                    double max_ang = ((BoneNode*) bone.node())->get_max_angle();

                    if (axis != LVector3::zero() && (rot_axis - axis).length_squared() > 0.5) {
                        // Clamp the rotation value:
                        ang = fmax(-max_ang, fmin(-min_ang, ang));
                    } else {
                        // Clamp the rotation value:
                        ang = fmax(min_ang, fmin(max_ang, ang));
                    }
                }

                q_new.set_from_axis_angle_rad(ang, rot_axis);

                bone.set_quat(armature, q_new);
            }
        }
    }

    sync_ik2p_local();
}
