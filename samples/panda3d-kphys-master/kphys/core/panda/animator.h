#ifndef PANDA_ANIMATOR_H
#define PANDA_ANIMATOR_H

#include "pandaNode.h"
#include "pmap.h"
#include "pvector.h"
#include "nodePath.h"

#include "kphys/core/panda/animation.h"
#include "kphys/core/panda/channel.h"


class EXPORT_CLASS AnimatorNode: public PandaNode {
PUBLISHED:
    AnimatorNode(const char* name);
    ~AnimatorNode();
    unsigned int get_num_channels();
    void add_channel(const char* name);
    PointerTo<Channel> get_channel(unsigned int i);
    PointerTo<Channel> get_channel(const char* name);
    void put_animation(const char* name, Animation* animation);
    PointerTo<Animation> get_animation(const char* name);
    void update(double dt);
    void apply(bool blend=true, bool interpolate=true);

private:
    NodePath _armature;
    pmap<std::string, PointerTo<Animation>> _animations;
    pvector<std::string> _channel_names;
    pmap<std::string, PointerTo<Channel>> _channels;

    static TypeHandle _type_handle;

public:
    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        PandaNode::init_type();
        register_type(_type_handle, "AnimatorNode", PandaNode::get_class_type());
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
