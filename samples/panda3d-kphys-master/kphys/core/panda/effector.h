#ifndef PANDA_EFFECTOR_H
#define PANDA_EFFECTOR_H

#include "pandaNode.h"
#include "transformState.h"

#ifdef CPPPARSER  // interrogate
#else  // normal compiler
#include "ik/ik.h"
#endif

#include "kphys/core/panda/ccdik.h"
#include "kphys/core/panda/ik.h"


class EXPORT_CLASS EffectorNode: public PandaNode {
PUBLISHED:
    explicit EffectorNode(
        const char* name, unsigned int chain_length=1, unsigned int priority=0);
    unsigned int get_chain_length();
    unsigned int get_priority();
    NodePath get_chain_root();
    double get_weight();
    void set_weight(double weight);

private:
    unsigned int _chain_length;
    unsigned int _priority;
    LVecBase3 _position;
    LQuaternion _rotation;
    double _weight;  // [IK] effector weight
    struct ik_effector_t* _ik_effector;  // [IK] effector
    static TypeHandle _type_handle;

public:
    struct ik_effector_t* get_ik_effector();
    unsigned int rebuild_ik(struct ik_solver_t* ik_solver, unsigned int node_id);
    void sync_p2ik_local();
    void sync_ik2p_local();
    void sync_ik2p_chain_reverse();
    void inverse_kinematics_ccd(
        double threshold=1e-2, unsigned int min_iterations=1, unsigned int max_iterations=10);

    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        PandaNode::init_type();
        register_type(_type_handle, "EffectorNode", PandaNode::get_class_type());
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
