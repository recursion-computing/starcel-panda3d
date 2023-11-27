#ifndef PANDA_SPRING_V1_H
#define PANDA_SPRING_V1_H

#ifdef CPPPARSER  // interrogate
BEGIN_PUBLISH
#endif

enum SpringDOF {  // Degree Of Freedom types:
    SPRING_DOF_TX = 0,  // translation along X axis
    SPRING_DOF_TY = 1,  // translation along Y axis
    SPRING_DOF_TZ = 2,  // translation along Z axis
    SPRING_DOF_RX = 3,  // rotation around X axis
    SPRING_DOF_RY = 4,  // rotation around Y axis
    SPRING_DOF_RZ = 5,  // rotation around Z axis
};

#ifdef CPPPARSER  // interrogate
END_PUBLISH
#endif

/* #define SpringConstraint SpringConstraint */
/* #include "kphys/core/panda/spring.h" */
/* #undef SpringConstraint */

#endif
