#ifndef PANDA_FRAME_H
#define PANDA_FRAME_H

#include "nodePath.h"
#include "typedReferenceCount.h"
#include "pmap.h"
#include "pvector.h"
#include "transformState.h"

#include "kphys/core/panda/types.h"

BEGIN_PUBLISH
enum TransformComponent {
    TRANSFORM_POS = 1 << 0,
    TRANSFORM_HPR = 1 << 1,
    TRANSFORM_QUAT = 1 << 2,
};
END_PUBLISH


class EXPORT_CLASS Frame: public TypedReferenceCount {
PUBLISHED:
    Frame();
    ~Frame();
    unsigned int get_num_transforms();
    const char* get_bone_name(unsigned int i);
    ConstPointerTo<TransformState> get_transform(unsigned int i);
    ConstPointerTo<TransformState> get_transform(const char* name);
    unsigned short get_transform_flags(const char* name);
    double get_transform_factor(const char* name);
    PointerTo<Frame> mix(PointerTo<Frame> frame_b, double factor=-1.0);

private:
    unsigned long _iframe;
    pvector<std::string> _bone_names;
    pmap<std::string, ConstPointerTo<TransformState>> _transforms;
    pmap<std::string, unsigned short> _transform_flags;
    pmap<std::string, double> _transform_factors;

    static TypeHandle _type_handle;

public:
    void add_transform(
        const char* name, ConstPointerTo<TransformState> transform,
        unsigned short flags, double factor=1.0);
    void add_transform(
        const char* name, ConstPointerTo<TransformState> transform,
        bool has_pos, bool has_hpr, bool has_quat, double factor=1.0);

    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        TypedReferenceCount::init_type();
        register_type(_type_handle, "Frame", TypedReferenceCount::get_class_type());
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
