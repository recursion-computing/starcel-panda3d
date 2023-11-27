#ifndef PANDA_SPRING_H
#define PANDA_SPRING_H

#ifdef CPPPARSER  // interrogate
#include <btBulletDynamicsCommon.h>  // panda3d parser-inc
class btGeneric6DofSpring2Constraint;
#else  // normal compiler
#include <BulletDynamics/ConstraintSolver/btGeneric6DofSpring2Constraint.h>
#endif

#include "bulletGenericConstraint.h"
#include "bulletRigidBodyNode.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846264338327
#endif


class EXPORT_CLASS SpringConstraint: public BulletConstraint {
PUBLISHED:
    SpringConstraint(
        const BulletRigidBodyNode* node_a,
        const BulletRigidBodyNode* node_b,
        const TransformState* frame_a,
        const TransformState* frame_b,
        bool use_frame_a_ref);
    ~SpringConstraint() {
        delete _constraint;
    }

    void set_spring(int dof, bool enabled);
    void set_stiffness(int dof, double value);
    void set_damping(int dof, double value);
    void set_limit(int dof, double min, double max);
    void set_equilibrium_point(int dof);
    void set_equilibrium_point(int dof, double value);

#ifdef USE_SPRING_V2
    void set_rotation_order(int order);
    void set_bounce(int dof, double value);

    void set_motor(int dof, bool enabled);
    void set_motor_servo(int dof, bool enabled);
    void set_target_velocity(int dof, double value);
    void set_servo_target(int dof, double value);
    void set_max_motor_force(int dof, double value);
#endif

public:
    virtual btTypedConstraint* ptr() const {
        return _constraint;
    }

private:
#ifdef USE_SPRING_V2
    btGeneric6DofSpring2Constraint *_constraint;
#else
    btGeneric6DofSpringConstraint *_constraint;
#endif
    static TypeHandle _type_handle;

public:
    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        BulletConstraint::init_type();
        register_type(
            _type_handle,
#ifdef USE_SPRING_V2
            "Spring2Constraint",
#else
            "SpringConstraint",
#endif
            BulletConstraint::get_class_type());
    }
    virtual TypeHandle get_type() const {
        return get_class_type();
    }
    virtual TypeHandle force_init_type() {
        init_type();
        return get_class_type();
    }
};

#endif
