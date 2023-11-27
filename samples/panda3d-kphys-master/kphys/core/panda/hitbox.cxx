#include "kphys/core/panda/hitbox.h"


TypeHandle HitboxNode::_type_handle;


HitboxNode::HitboxNode(const char *name):
    BulletGhostNode(name) {}
