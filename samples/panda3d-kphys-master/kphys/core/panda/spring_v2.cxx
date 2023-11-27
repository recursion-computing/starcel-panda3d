#include "kphys/core/panda/spring_v2.h"

#define SPRING_CONSTRAINT Spring2Constraint
#define SPRING_CONSTRAINT_NAME "Spring2Constraint"
#define USE_SPRING_V2 1
#include "kphys/core/panda/spring.cxx"

void SPRING_CONSTRAINT::set_rotation_order(int order) {
    _constraint->setRotationOrder((RotateOrder) order);
}

void SPRING_CONSTRAINT::set_bounce(int dof, double value) {
    _constraint->setBounce(dof, (btScalar) value);
}

void SPRING_CONSTRAINT::set_motor(int dof, bool enabled) {
    _constraint->enableMotor(dof, enabled);
}

void SPRING_CONSTRAINT::set_motor_servo(int dof, bool enabled) {
    _constraint->setServo(dof, enabled);
}

void SPRING_CONSTRAINT::set_target_velocity(int dof, double value) {
    _constraint->setTargetVelocity(dof, (btScalar) value);
}

void SPRING_CONSTRAINT::set_servo_target(int dof, double value) {
    _constraint->setServoTarget(dof, (btScalar) value);
}

void SPRING_CONSTRAINT::set_max_motor_force(int dof, double value) {
    _constraint->setMaxMotorForce(dof, (btScalar) value);
}

#undef SPRING_CONSTRAINT
#undef SPRING_CONSTRAINT_NAME
#undef USE_SPRING_V2
