#ifndef PANDA_ANIMATION_H
#define PANDA_ANIMATION_H

#include "namable.h"
#include "pvector.h"
#include "typedReferenceCount.h"

#include "kphys/core/panda/frame.h"


class EXPORT_CLASS Animation: public TypedReferenceCount, public Namable {
PUBLISHED:
    Animation(const char* name);
    ~Animation();
    unsigned long get_num_frames();
    PointerTo<Frame> get_frame(unsigned long i);
    double get_frame_time();
    void set_frame_time(double frame_time);
    bool can_blend_in();
    bool can_blend_out();
    bool is_loop();
    bool is_manual();
    void set_blending_mode(bool blend_in, bool blend_out);
    void set_loop(bool loop);
    void set_manual(bool manual);

private:
    unsigned long _get_frame_index(long frame);
    bool _blend_in;
    bool _blend_out;
    bool _is_loop;
    bool _is_manual;

    static TypeHandle _type_handle;

protected:
    pvector<PointerTo<Frame>> _motion;
    double _frame_time;

public:
    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        TypedReferenceCount::init_type();
        register_type(_type_handle, "Animation", TypedReferenceCount::get_class_type());
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
