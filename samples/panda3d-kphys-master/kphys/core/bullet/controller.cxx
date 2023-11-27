#include <kphys/core/bullet/controller.h>


btController::btController(
        btPairCachingGhostObject* ghostObject, btConvexShape* convexShape,
        btScalar stepHeight, const btVector3 & upAxis):
    btKinematicCharacterController(ghostObject, convexShape, stepHeight, upAxis) {
    _is_simulated = true;
}

btScalar btController::get_vertical_velocity() {
    return m_verticalVelocity;
}

void btController::set_vertical_velocity(btScalar v) {
    m_verticalVelocity = v;
}

bool btController::get_jumping() {
    return m_wasJumping;
}

void btController::set_jumping(bool jumping) {
    m_wasJumping = jumping;
}

bool btController::get_simulated() {
    return _is_simulated;
}

void btController::set_simulated(bool simulated) {
    _is_simulated = simulated;
}

void btController::jump () {
    m_verticalVelocity = m_jumpSpeed;
    m_wasJumping = true;
}

void btController::updateAction(btCollisionWorld* collisionWorld, btScalar deltaTime) {
    if (_is_simulated) {
        preStep(collisionWorld);
        playerStep(collisionWorld, deltaTime);
    }
}
