#ifndef BULLET_CONTROLLER_H
#define BULLET_CONTROLLER_H

#ifdef CPPPARSER  // interrogate
#include <btBulletDynamicsCommon.h>  // panda3d parser-inc
#else  // normal compiler
#include <BulletDynamics/Character/btKinematicCharacterController.h>
#endif


class btController : public btKinematicCharacterController {
public:
    BT_DECLARE_ALIGNED_ALLOCATOR();

    btController(
        btPairCachingGhostObject* ghostObject, btConvexShape* convexShape,
        btScalar stepHeight, const btVector3 & upAxis = btVector3(1.0,0.0,0.0));

    btScalar get_vertical_velocity();
    void set_vertical_velocity(btScalar v);

    bool get_jumping();
    void set_jumping(bool jumping);

    bool get_simulated();
    void set_simulated(bool simulated);

    void jump();
    virtual void updateAction(btCollisionWorld* collisionWorld, btScalar deltaTime);

private:
    bool _is_simulated;
};

#endif
