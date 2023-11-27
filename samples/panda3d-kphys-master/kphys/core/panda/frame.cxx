#include "kphys/core/panda/frame.h"
#include "kphys/core/panda/channel.h"

#define QUAT_LERP quat_nlerp


TypeHandle Frame::_type_handle;


LVecBase3 mix3(const LVecBase3& a, const LVecBase3& b, double factor) {
    return LVecBase3(
        a.get_x() - factor * (a.get_x() - b.get_x()),
        a.get_y() - factor * (a.get_y() - b.get_y()),
        a.get_z() - factor * (a.get_z() - b.get_z()));
}

LQuaternion quat_nlerp(const LQuaternion& a, const LQuaternion& b, double factor) {
    LQuaternion q_a = a;
    LQuaternion q_b = b;
    if (q_a.dot(q_b) < 0) {  // negate quat if dot product is negative
        q_b.set_r(q_b.get_r() * -1);
        q_b.set_i(q_b.get_i() * -1);
        q_b.set_j(q_b.get_j() * -1);
        q_b.set_k(q_b.get_k() * -1);
    }

    LQuaternion q = LQuaternion(
        q_a.get_r() - factor * (q_a.get_r() - q_b.get_r()),
        q_a.get_i() - factor * (q_a.get_i() - q_b.get_i()),
        q_a.get_j() - factor * (q_a.get_j() - q_b.get_j()),
        q_a.get_k() - factor * (q_a.get_k() - q_b.get_k()));
    // q.normalize();
    return q;
}

LQuaternion quat_slerp(const LQuaternion& a, const LQuaternion& b, double factor) {
    LQuaternion q_a = a;
    LQuaternion q_b = b;
    // https://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions/slerp/index.htm
    // quaternion to return
    LQuaternion q;
    // calculate angle between them.
    double cos_half_theta = q_a.dot(q_b);
    // you may need to add the following code after cosHalfTheta is calculated.
    if (cos_half_theta < 0) {
        q_b.set_r(q_b.get_r() * -1);
        q_b.set_i(q_b.get_i() * -1);
        q_b.set_j(q_b.get_j() * -1);
        cos_half_theta *= -1;
    }
    // if qa=qb or qa=-qb then theta = 0 and we can return qa
    if (fabs(cos_half_theta) >= 1.0) {
        return q_a;
    }
    // calculate temporary values.
    float half_theta = acos(cos_half_theta);
    float sin_half_theta = sqrt(1.0 - cos_half_theta * cos_half_theta);
    // if theta = 180 degrees then result is not fully defined
    // we could rotate around any axis normal to qa or qb
    if (fabs(sin_half_theta) < 0.001) {
        q.set_r(q_a.get_r() * 0.5 + q_b.get_r() * 0.5);
        q.set_i(q_a.get_i() * 0.5 + q_b.get_i() * 0.5);
        q.set_j(q_a.get_j() * 0.5 + q_b.get_j() * 0.5);
        q.set_k(q_a.get_k() * 0.5 + q_b.get_k() * 0.5);
        return q;
    }
    float ratio_a = sin((1 - factor) * half_theta) / sin_half_theta;
    float ratio_b = sin(factor * half_theta) / sin_half_theta;
    // calculate quaternion.
    q.set_r(q_a.get_r() * ratio_a + q_b.get_r() * ratio_b);
    q.set_i(q_a.get_i() * ratio_a + q_b.get_i() * ratio_b);
    q.set_j(q_a.get_j() * ratio_a + q_b.get_j() * ratio_b);
    q.set_k(q_a.get_k() * ratio_a + q_b.get_k() * ratio_b);
    // q.normalize();
    return q;
}


Frame::Frame() {}

Frame::~Frame() {
    _bone_names.clear();
    _transforms.clear();
    _transform_flags.clear();
    _transform_factors.clear();
}

void Frame::add_transform(
        const char* name, ConstPointerTo<TransformState> transform,
        unsigned short flags, double factor) {
    if (get_transform(name) != NULL)
        return;

    std::string s = std::string(name);
    _bone_names.push_back(s);
    _transforms[s] = transform;
    _transform_flags[s] = flags;
    _transform_factors[s] = factor;
}

void Frame::add_transform(
        const char* name, ConstPointerTo<TransformState> transform,
        bool has_pos, bool has_hpr, bool has_quat, double factor) {
    unsigned short flags = 0;
    if (has_pos)
        flags |= TRANSFORM_POS;
    if (has_hpr)
        flags |= TRANSFORM_HPR;
    if (has_quat)
        flags |= TRANSFORM_QUAT;
    add_transform(name, transform, flags, factor);
}

unsigned int Frame::get_num_transforms() {
    return _transforms.size();
}

const char* Frame::get_bone_name(unsigned int i) {
    return _bone_names[i].c_str();
}

ConstPointerTo<TransformState> Frame::get_transform(unsigned int i) {
    const char* bone_name = get_bone_name(i);
    return get_transform(bone_name);
}

ConstPointerTo<TransformState> Frame::get_transform(const char* name) {
    std::string s = std::string(name);
    if (_transforms.find(s) == _transforms.end())
        return NULL;
    return _transforms[s];
}

unsigned short Frame::get_transform_flags(const char* name) {
    std::string s = std::string(name);
    if (_transform_flags.find(s) == _transform_flags.end())
        return 0;
    return _transform_flags[s];
}

double Frame::get_transform_factor(const char* name) {
    std::string s = std::string(name);
    if (_transform_factors.find(s) == _transform_factors.end())
        return 1.0;
    return _transform_factors[s];
}

PointerTo<Frame> Frame::mix(PointerTo<Frame> frame_b, double factor) {
    if (factor == 0.0)
        return this;
    else if (factor >= 1.0)
        return frame_b;

    PointerTo<Frame> frame = new Frame();

    for (unsigned int s = 0; s < NUM_SLOTS; s++) {
        unsigned int bsize;
        if (s == SLOT_A)
            bsize = get_num_transforms();
        else
            bsize = frame_b->get_num_transforms();

        for (unsigned int b = 0; b < bsize; b++) {
            const char* bone_name;
            if (s == SLOT_A)
                bone_name = get_bone_name(b);
            else
                bone_name = frame_b->get_bone_name(b);

            if (frame->get_transform(bone_name) != NULL)
                continue;

            ConstPointerTo<TransformState> transform_a = get_transform(bone_name);
            ConstPointerTo<TransformState> transform_b = frame_b->get_transform(bone_name);
            unsigned short flags_a = get_transform_flags(bone_name);
            unsigned short flags_b = frame_b->get_transform_flags(bone_name);
            double factor_a = get_transform_factor(bone_name);
            double factor_b = frame_b->get_transform_factor(bone_name);
            unsigned short flags = flags_a & flags_b;
            double cfactor = (factor < 0.0) ? factor_b : factor;

            if (transform_a != NULL && cfactor < 0.001) {
                frame->add_transform(bone_name, transform_a, flags_a);
                continue;
            }

            if (transform_b != NULL && cfactor > 0.999) {
                frame->add_transform(bone_name, transform_b, flags_b);
                continue;
            }

            if (transform_a != NULL && transform_b != NULL) {
                LVecBase3 pos, hpr;
                LQuaternion quat;
                bool has_pos = false, has_hpr = false, has_quat = false;

                if (flags & TRANSFORM_POS) {
                    pos = mix3(transform_a->get_pos(), transform_b->get_pos(), cfactor);
                    has_pos = true;
                }
                if (flags & TRANSFORM_HPR) {
                    hpr = mix3(transform_a->get_hpr(), transform_b->get_hpr(), cfactor);
                    has_hpr = true;
                }
                if (flags & TRANSFORM_QUAT) {
                    quat = QUAT_LERP(transform_a->get_quat(), transform_b->get_quat(), cfactor);
                    has_quat = true;
                }

                ConstPointerTo<TransformState> transform = NULL;

                if (has_pos && has_hpr && !has_quat)
                    transform = TransformState::make_pos_hpr(pos, hpr);
                else if (has_pos && !has_hpr && has_quat)
                    // there is no make_pos_quat() method
                    transform = TransformState::make_pos_quat_scale(
                        pos, quat, LVecBase3(1, 1, 1));
                else if (has_pos && !has_hpr && !has_quat)
                    transform = TransformState::make_pos(pos);
                else if (!has_pos && has_hpr && !has_quat)
                    transform = TransformState::make_hpr(hpr);
                else if (!has_pos && !has_hpr && has_quat)
                    transform = TransformState::make_quat(quat);

                if (transform != NULL) {
                      frame->add_transform(
                          bone_name, transform, has_pos, has_hpr, has_quat);
                }
            }
        }
    }

    return frame;
}
