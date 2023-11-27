#include "kphys/core/panda/converters.h"


/**
 * Convert Panda3D LVecBase3 to IK Vec3.
 */
ik_vec3_t LVecBase3_to_IKVec3(const LVecBase3& panda) {
    ik_vec3_t ret;
    ret.x = panda.get_x();
    ret.y = panda.get_y();
    ret.z = panda.get_z();
    return ret;
}

/**
 * Convert Panda3D LQuaternion to IK Quat.
 */
ik_quat_t LQuaternion_to_IKQuat(const LQuaternion& panda) {
    ik_quat_t ret;
    ret.x = panda.get_i();
    ret.y = panda.get_j();
    ret.z = panda.get_k();
    ret.w = panda.get_r();
    return ret;
}

/**
 * Convert IK Vec3 to Panda3D LVecBase3.
 */
LVecBase3 IKVec3_to_LVecBase3(const ik_vec3_t& ik) {
  return LVecBase3(ik.x, ik.y, ik.z);
}

/**
 * Convert IK Quat to Panda3D LQuaternion.
 */
LQuaternion IKQuat_to_LQuaternion(const ik_quat_t& ik) {
    return LQuaternion(ik.w, ik.x, ik.y, ik.z);  // r, i, j, k
}
