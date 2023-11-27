#include "kphys/core/panda/animator.h"
#include "kphys/core/panda/armature.h"

#include "nodePath.h"


TypeHandle AnimatorNode::_type_handle;

AnimatorNode::AnimatorNode(const char* name): PandaNode(name) {}

AnimatorNode::~AnimatorNode() {
    _animations.clear();
    _channel_names.clear();
    _channels.clear();
}

unsigned int AnimatorNode::get_num_channels() {
    return _channels.size();
}

/**
   Create a new animation channel.
*/
void AnimatorNode::add_channel(const char* name) {
    std::string s = std::string(name);
    _channel_names.push_back(s);
    _channels[s] = new Channel(name);
}

/**
   Get an animation channel.
*/
PointerTo<Channel> AnimatorNode::get_channel(unsigned int i) {
    return _channels[_channel_names[i]];
}

/**
   Get an animation channel.
*/
PointerTo<Channel> AnimatorNode::get_channel(const char* name) {
    std::string s = std::string(name);
    if (_channels.find(s) == _channels.end())
        return NULL;
    return _channels[s];
}

/**
   Put a reusable animation in the storage.
*/
void AnimatorNode::put_animation(const char* name, Animation* animation) {
    std::string s = std::string(name);
    _animations[s] = animation;
}

/**
   Get a reusable animation from the storage.
*/
PointerTo<Animation> AnimatorNode::get_animation(const char* name) {
    std::string s = std::string(name);
    if (_animations.find(s) == _animations.end())
        return NULL;
    return _animations[s];
}

void AnimatorNode::update(double dt) {
    unsigned int csize = get_num_channels();
    for (unsigned int c = 0; c < csize; c++) {
        PointerTo<Channel> channel = get_channel(c);
        channel->update(dt);
    }
}

void AnimatorNode::apply(bool blend, bool interpolate) {
    PointerTo<Frame> frames[NUM_SLOTS];
    for (unsigned int s = 0; s < NUM_SLOTS; s++) {
        frames[s] = new Frame();

        // merge all channels into the singe frame
        unsigned int csize = get_num_channels();
        for (unsigned int c = 0; c < csize; c++) {
            PointerTo<Channel> channel = get_channel(c);

            PointerTo<Frame> frame = channel->get_frame(s, interpolate);
            if (frame == NULL)
                continue;

            double cfactor = channel->get_factor();
            if (!blend)
                cfactor = 1.0;

            if (s == SLOT_A)
                cfactor = 1.0 - cfactor;

            // copy transforms
            unsigned int bsize = frame->get_num_transforms();
            for (unsigned int b = 0; b < bsize; b++) {
                const char* bone_name = frame->get_bone_name(b);
                if (!channel->is_bone_enabled(bone_name))
                    continue;

                if (frames[s]->get_transform(bone_name) != NULL)
                    continue;

                ConstPointerTo<TransformState> transform = frame->get_transform(bone_name);
                if (transform == NULL)
                    continue;

                unsigned short flags = frame->get_transform_flags(bone_name);
                frames[s]->add_transform(bone_name, transform, flags, cfactor);
            }
        }
    }

    PointerTo<Frame> frame = frames[SLOT_A]->mix(frames[SLOT_B]);

    NodePath animator = NodePath::any_path(this);
    NodePathCollection armatures = animator.find_all_matches("**/+ArmatureNode");
    for (int i = 0; i < armatures.get_num_paths(); i++) {
        NodePath np = armatures.get_path(i);
        ((ArmatureNode*) np.node())->apply(frame);
        break;
    }
}
