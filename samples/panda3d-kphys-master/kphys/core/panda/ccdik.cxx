#include <stdlib.h>

#include "transformState.h"

#include "kphys/core/panda/ccdik.h"


/**
 * Swing-Twist decomposition based on:
 * https://stackoverflow.com/questions/3684269/component-of-a-quaternion-rotation-around-an-axis
 * Decompose the rotation to 2 parts.
 * 1. Twist - rotation around the "twistAxis" vector
 * 2. Swing - rotation around axis that is perpendicular to "twistAxis" vector
 * The rotation can be composed back by
 * rotation = swing * twist
 *
 * has singularity in case of swing_rotation close to 180 degrees rotation.
 * if the input quaternion is of non-unit length, the outputs are non-unit as well
 * otherwise, outputs are both unit
 */
LMatrix4 swing_twist_decomposition(LQuaternion rotation, LVector3 twist_axis) {
    LVector3 ra = LVector3f(rotation.get_i(), rotation.get_j(), rotation.get_k());
    LVecBase3 p = ra.project(twist_axis);  // return projection v1 onto v2
    LQuaternion twist = LQuaternion(rotation.get_r(), p.get_x(), p.get_y(), p.get_z());
    twist.normalize();
    LQuaternion swing = rotation * twist.conjugate();
    LMatrix4 result;
    result.set_row(0, (LVecBase4) swing);
    result.set_row(1, (LVecBase4) twist);
    return result;
}
