#ifndef PANDA_CONVERTERS_H
#define PANDA_CONVERTERS_H

#include "transformState.h"

#ifdef CPPPARSER  // interrogate
union ik_quat_t;
union ik_vec3_t;
#else  // normal compiler
#include "ik/quat.h"
#include "ik/vec3.h"
#endif


// Conversion from Panda3D to IK
ik_vec3_t LVecBase3_to_IKVec3(const LVecBase3& panda);
ik_quat_t LQuaternion_to_IKQuat(const LQuaternion& panda);

// Conversion from IK to Panda3D
LVecBase3 IKVec3_to_LVecBase3(const ik_vec3_t& ik);
LQuaternion IKQuat_to_LQuaternion(const ik_quat_t& ik);

#endif
