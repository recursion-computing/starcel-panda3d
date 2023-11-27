#ifndef PANDA_SPRING_V2_H
#define PANDA_SPRING_V2_H

#ifdef CPPPARSER  // interrogate
BEGIN_PUBLISH
#endif

enum SpringRotateOrder {
    SPRING_RO_XYZ = 0,
    SPRING_RO_XZY = 1,
    SPRING_RO_YXZ = 2,
    SPRING_RO_YZX = 3,
    SPRING_RO_ZXY = 4,
    SPRING_RO_ZYX = 5,
};

#ifdef CPPPARSER  // interrogate
END_PUBLISH
#endif

#define SPRING_CONSTRAINT Spring2Constraint
#define USE_SPRING_V2 1
#include "kphys/core/panda/spring.h"
#undef SPRING_CONSTRAINT
#undef USE_SPRING_V2

#endif
