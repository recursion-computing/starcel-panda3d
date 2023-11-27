#include "kphys/core/panda/controller.h"


static const btVector3 up_vectors[3] = {btVector3(1.0f, 0.0f, 0.0f), btVector3(0.0f, 1.0f, 0.0f), btVector3(0.0f, 0.0f, 1.0f)};

TypeHandle ControllerNode::_type_handle;


ControllerNode::ControllerNode(BulletShape *shape, PN_stdfloat step_height, const char *name):
    BulletCharacterControllerNode(shape, step_height, name) {
    delete _character;

    btConvexShape *convex = (btConvexShape *)(shape->ptr());

    // custom Bullet Physics character controller
    _character = new btController(_ghost, convex, step_height, up_vectors[get_default_up_axis()]);
    _character->setGravity(up_vectors[get_default_up_axis()] * -(btScalar)9.81f);
}

PN_stdfloat ControllerNode::get_vertical_velocity() {
    return (PN_stdfloat) ((btController*) _character)->get_vertical_velocity();
}

void ControllerNode::set_vertical_velocity(PN_stdfloat v) {
    ((btController*) _character)->set_vertical_velocity((btScalar) v);
}

bool ControllerNode::get_jumping() {
    return ((btController*) _character)->get_jumping();
}

void ControllerNode::set_jumping(bool jumping) {
    ((btController*) _character)->set_jumping(jumping);
}

bool ControllerNode::get_simulated() {
    return ((btController*) _character)->get_simulated();
}

void ControllerNode::set_simulated(bool simulated) {
    ((btController*) _character)->set_simulated(simulated);
}
