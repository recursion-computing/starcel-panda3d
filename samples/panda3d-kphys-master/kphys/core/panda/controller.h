#ifndef PANDA_CONTROLLER_H
#define PANDA_CONTROLLER_H

#include "bulletCharacterControllerNode.h"

#include "kphys/core/bullet/controller.h"


class EXPORT_CLASS ControllerNode: public BulletCharacterControllerNode {
PUBLISHED:
    explicit ControllerNode(
        BulletShape *shape, PN_stdfloat step_height,
        const char *name="character");

    PN_stdfloat get_vertical_velocity();
    void set_vertical_velocity(PN_stdfloat v);

    bool get_jumping();
    void set_jumping(bool jumping);

    bool get_simulated();
    void set_simulated(bool simulated);

private:
    static TypeHandle _type_handle;

public:
    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        BulletCharacterControllerNode::init_type();
        register_type(
            _type_handle, "ControllerNode",
            BulletCharacterControllerNode::get_class_type());
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
