#ifndef CORE_PROGRESS_BAR_H
#define CORE_PROGRESS_BAR_H

#include "pandabase.h"
#include "pgItem.h"


class ProgressBar: public PGItem {
PUBLISHED:
    ProgressBar(const std::string &name = "");
    ~ProgressBar();

protected:
    ProgressBar(const ProgressBar &copy);

public:
    virtual PandaNode *make_copy() const;
    virtual bool cull_callback(CullTraverser *trav, CullTraverserData &data);

PUBLISHED:
    void setup(PN_stdfloat width, PN_stdfloat height, PN_stdfloat range);

    void set_range(PN_stdfloat range);
    PN_stdfloat get_range() const;

    void set_value(PN_stdfloat value);
    PN_stdfloat get_value() const;

    PN_stdfloat get_percent() const;

    void set_bar_style(const PGFrameStyle &style);
    PGFrameStyle get_bar_style() const;

private:
    void update();
    NodePath generate_into(const NodePath &parent, const LVecBase4 &frame, int sort=0);
    PT(PandaNode) generate_flat_geom(const LVecBase4 &frame);
    PT(PandaNode) generate_texture_border_geom(const LVecBase4 &frame);

    PN_stdfloat _range, _value;
    int _bar_state;
    PGFrameStyle _bar_style;
    NodePath _bar;

public:
    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        PGItem::init_type();
        register_type(_type_handle, "ProgressBar", PGItem::get_class_type());
    }
    virtual TypeHandle get_type() const {
        return get_class_type();
    }
    virtual TypeHandle force_init_type() {init_type(); return get_class_type();}

private:
    static TypeHandle _type_handle;
};

#endif
