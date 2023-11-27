#include "kphys/core/panda/animation.h"


TypeHandle Animation::_type_handle;

Animation::Animation(const char* name): Namable(name) {
    _blend_in = true;
    _blend_out = true;
    _is_loop = true;
    _is_manual = false;
}

Animation::~Animation() {
    _motion.clear();
}

unsigned long Animation::_get_frame_index(long frame) {
    unsigned long num_frames = get_num_frames();
    while (frame < 0)
        frame = num_frames - frame;
    while (frame >= num_frames)
        frame -= num_frames;
    return (unsigned long) frame;
}

unsigned long Animation::get_num_frames() {
    return _motion.size();
}

PointerTo<Frame> Animation::get_frame(unsigned long i) {
    return _motion[_get_frame_index(i)];
}

/**
   Get the duration of frame.
*/
double Animation::get_frame_time() {
    return _frame_time;
}

/**
   Set the duration of frame.
*/
void Animation::set_frame_time(double frame_time) {
    _frame_time = frame_time;
}

/**
   Check if another animation can blend in into this animation.
*/
bool Animation::can_blend_in() {
    return _blend_in;
}

/**
   Check if this animation can blend out into another animation.
*/
bool Animation::can_blend_out() {
    return _blend_out;
}

/**
   Check if this animation is looped.
*/
bool Animation::is_loop() {
    return _is_loop;
}

/**
   Check if this is a manually controlled animation,
   which doesn't adnvance frames by time.
*/
bool Animation::is_manual() {
    return _is_manual;
}

/**
   Set animation blending mode.
   blend_in - another animation can blend in into this animation
   blend_out - this animation can blend out into another animation
*/
void Animation::set_blending_mode(bool blend_in, bool blend_out) {
    _blend_in = blend_in;
    _blend_out = blend_out;
}

/**
   Set loop mode.
*/
void Animation::set_loop(bool loop) {
    _is_loop = loop;
}

/**
   Set manually controlled animation flag for animations,
   which doesn't adnvance frames by time.
*/
void Animation::set_manual(bool manual) {
    _is_manual = manual;
}
