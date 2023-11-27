#ifndef PANDA_HITBOX_H
#define PANDA_HITBOX_H

#include "bulletGhostNode.h"


class EXPORT_CLASS HitboxNode: public BulletGhostNode {
PUBLISHED:
    explicit HitboxNode(const char *name="ghost");

private:
    static TypeHandle _type_handle;

public:
    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        BulletGhostNode::init_type();
        register_type(
            _type_handle, "HitboxNode",
            BulletGhostNode::get_class_type());
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
