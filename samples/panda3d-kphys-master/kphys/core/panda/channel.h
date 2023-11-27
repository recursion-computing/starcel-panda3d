#ifndef PANDA_CHANNEL_H
#define PANDA_CHANNEL_H

#include "nodePath.h"
#include "pmap.h"
#include "typedReferenceCount.h"

#include "kphys/core/panda/animation.h"

#ifndef NDEBUG
#define DEBUG_KPHYS
#endif

#define NUM_SLOTS 2
/* #define SLOT_A 0 */
/* #define SLOT_B 1 */


BEGIN_PUBLISH
enum SLOT {
    SLOT_A = 0,
    SLOT_B = 1,
};
END_PUBLISH

class EXPORT_CLASS Channel: public TypedReferenceCount, public Namable {
PUBLISHED:
    Channel(const char* name);
    ~Channel();
    double get_factor();
    void set_blending_time(double t);
    double get_frame_index(unsigned short slot);
    void set_frame_index(unsigned short slot, double frame);
    PointerTo<Frame> get_frame(unsigned short slot, bool interpolate=true);
    PointerTo<Animation> get_animation(unsigned short slot);
    void ls();
    void push_animation(PointerTo<Animation> animation);
    void switch_animation();
    void update(double dt);
    void include_bone(const char* name);
    void exclude_bone(const char* name);
    unsigned int get_num_included_bones();
    unsigned int get_num_excluded_bones();
    bool is_bone_included(const char* name);
    bool is_bone_excluded(const char* name);
    bool is_bone_enabled(const char* name);

private:
    PointerTo<Animation> _animations[2];
    double _frame_indices[2];
    double _factor;
    double _blending_time;
    pmap<std::string, bool> _include_bones;
    pmap<std::string, bool> _exclude_bones;

    static TypeHandle _type_handle;

public:
    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        TypedReferenceCount::init_type();
        register_type(_type_handle, "Channel", TypedReferenceCount::get_class_type());
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
