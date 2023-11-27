#ifndef PANDA_BONE_H
#define PANDA_BONE_H

/* https://docs.microsoft.com/en-us/cpp/c-runtime-library/math-constants?view=msvc-170 */
#define _USE_MATH_DEFINES // for C
#include <math.h>

#include "pandaNode.h"

#ifdef CPPPARSER  // interrogate
#else  // normal compiler
#include "ik/ik.h"
#endif

#include "kphys/core/panda/ik.h"


class EXPORT_CLASS BoneNode: public PandaNode {
PUBLISHED:
    explicit BoneNode(const char* name, unsigned int bone_id);
    unsigned int get_bone_id();
    void set_hinge_constraint(const LVecBase3& axis, double min_ang=-M_PI, double max_ang=M_PI);
    void set_ball_constraint(double min_ang=-M_PI, double max_ang=M_PI);
    bool is_static();
    void set_static(bool is_static);
    LVector3 get_axis();
    double get_min_angle();
    double get_max_angle();

private:
    unsigned int _bone_id;
    LVector3 _axis;  // [CCDIK] constraint axis
    double _min_ang;  // [CCDIK] min constraint angle
    double _max_ang;  // [CCDIK] max constraint angle
    bool _is_static;  // [CCDIK]
    struct ik_node_t* _ik_node;  // [IK] node
    static TypeHandle _type_handle;

public:
    struct ik_node_t* get_ik_node();
    unsigned int rebuild_ik_recursive(struct ik_solver_t* ik_solver, unsigned int node_id);
    void sync_p2ik_recursive();
    void sync_ik2p_local();

    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        PandaNode::init_type();
        register_type(_type_handle, "BoneNode", PandaNode::get_class_type());
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
