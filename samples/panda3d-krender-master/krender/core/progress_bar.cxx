#include "colorAttrib.h"
#include "geom.h"
#include "geomNode.h"
#include "geomTristrips.h"
#include "geomVertexWriter.h"
#include "nodePath.h"
#include "pandaNode.h"
#include "pgMouseWatcherParameter.h"
#include "pointerTo.h"
#include "renderState.h"
#include "shadeModelAttrib.h"
#include "textureAttrib.h"
#include "throw_event.h"
#include "transparencyAttrib.h"

#include "krender/core/progress_bar.h"


TypeHandle ProgressBar::_type_handle;


ProgressBar::ProgressBar(const std::string &name) : PGItem(name) {
    set_cull_callback();

    _range = 100.0;
    _value = 0.0;
    _bar_state = -1;
}

ProgressBar::~ProgressBar() {}

ProgressBar::ProgressBar(const ProgressBar &copy):
        PGItem(copy),
        _range(copy._range),
        _value(copy._value) {
    _bar_state = -1;
}

PandaNode *ProgressBar::make_copy() const {
    LightReMutexHolder holder(_lock);
    return new ProgressBar(*this);
}

bool ProgressBar::cull_callback(CullTraverser *trav, CullTraverserData &data) {
    LightReMutexHolder holder(_lock);
    update();
    return PGItem::cull_callback(trav, data);
}

void ProgressBar::setup(PN_stdfloat width, PN_stdfloat height, PN_stdfloat range) {
    LightReMutexHolder holder(_lock);
    set_state(0);
    clear_state_def(0);

    set_frame(-0.5f * width, 0.5f * width, -0.5f * height, 0.5f * height);

    PN_stdfloat bevel = 0.05f;

    PGFrameStyle style;
    style.set_width(bevel, bevel);

    style.set_color(0.6f, 0.6f, 0.6f, 1.0f);
    style.set_type(PGFrameStyle::T_flat);
    set_frame_style(0, style);

    style.set_color(0.8f, 0.8f, 0.8f, 1.0f);
    style.set_type(PGFrameStyle::T_flat);
    set_bar_style(style);
}

void ProgressBar::set_range(PN_stdfloat range) {
    LightReMutexHolder holder(_lock);
    _range = range;
    _bar_state = -1;
}

PN_stdfloat ProgressBar::get_range() const {
    LightReMutexHolder holder(_lock);
    return _range;
}

void ProgressBar::set_value(PN_stdfloat value) {
    LightReMutexHolder holder(_lock);
    _value = value;
    _bar_state = -1;
}

PN_stdfloat ProgressBar::get_value() const {
    LightReMutexHolder holder(_lock);
    return _value;
}

PN_stdfloat ProgressBar::get_percent() const {
    LightReMutexHolder holder(_lock);
    return (_value / _range) * 100.0f;
}

void ProgressBar::set_bar_style(const PGFrameStyle &style) {
    LightReMutexHolder holder(_lock);
    _bar_style = style;
    _bar_state = -1;
}

PGFrameStyle ProgressBar::get_bar_style() const {
    LightReMutexHolder holder(_lock);
    return _bar_style;
}

void ProgressBar::update() {
    LightReMutexHolder holder(_lock);
    int state = get_state();

    // If the bar was last drawn in this state and is still current, we don't
    // have to draw it again.
    if (_bar_state == state) {
        return;
    }

    // Remove the old bar geometry, if any.
    _bar.remove_node();

    // Now create new bar geometry.
    if ((_value != 0.0f) && (_range != 0.0f)) {
        NodePath &root = get_state_def(state);
        nassertv(!root.is_empty());

        PGFrameStyle style = get_frame_style(state);
        const LVecBase4 &frame = get_frame();
        const LVecBase2 &width = style.get_width();

        // Put the bar within the item's frame's border.
        LVecBase4 bar_frame(frame[0] + width[0],
                            frame[1] - width[0],
                            frame[2] + width[1],
                            frame[3] - width[1]);

        // And scale the bar according to our value.
        PN_stdfloat frac = _value / _range;
        frac = std::max(std::min(frac, (PN_stdfloat)1.0), (PN_stdfloat)0.0);
        bar_frame[1] = bar_frame[0] + frac * (bar_frame[1] - bar_frame[0]);

        // _bar = _bar_style.generate_into(root, bar_frame, 1);
        _bar = generate_into(root, bar_frame, 1);
    }

    // Indicate that the bar is current for this state.
    _bar_state = state;
}

NodePath ProgressBar::generate_into(
        const NodePath &parent, const LVecBase4 &frame,
        int sort) {
    PT(PandaNode) new_node;

    LVecBase2 visible_scale = _bar_style.get_visible_scale();
    LColor color = _bar_style.get_color();
    LPoint2 center((frame[0] + frame[1]) / 2.0f,
                   (frame[2] + frame[3]) / 2.0f);
    LVecBase4 scaled_frame
        ((frame[0] - center[0]) * visible_scale[0] + center[0],
         (frame[1] - center[0]) * visible_scale[0] + center[0],
         (frame[2] - center[1]) * visible_scale[1] + center[1],
         (frame[3] - center[1]) * visible_scale[1] + center[1]);

    switch (_bar_style.get_type()) {
    case PGFrameStyle::T_none:
        return NodePath();

    case PGFrameStyle::T_flat:
        new_node = generate_flat_geom(scaled_frame);
        break;

    case PGFrameStyle::T_texture_border:
        new_node = generate_texture_border_geom(scaled_frame);
        break;

    default:
        break;
    }

    if (new_node != nullptr && color[3] != 1.0f) {
        // We've got some alpha on the color; we need transparency.
        new_node->set_attrib(TransparencyAttrib::make(TransparencyAttrib::M_alpha));
    }

    // Adding the node to the parent keeps the reference count.
    return parent.attach_new_node(new_node, sort);
}

PT(PandaNode) ProgressBar::generate_flat_geom(const LVecBase4 &frame) {
    PT(GeomNode) gnode = new GeomNode("flat");

    PN_stdfloat left = frame[0];
    PN_stdfloat right = frame[1];
    PN_stdfloat bottom = frame[2];
    PN_stdfloat top = frame[3];

    CPT(GeomVertexFormat) format;
    if (_bar_style.has_texture()) {
        format = GeomVertexFormat::get_v3t2();
    } else {
        format = GeomVertexFormat::get_v3();
    }

    PT(GeomVertexData) vdata = new GeomVertexData
        ("PGFrame", format, Geom::UH_static);

    GeomVertexWriter vertex(vdata, InternalName::get_vertex());
    vertex.add_data3(LPoint3::rfu(left, 0.0f, top));
    vertex.add_data3(LPoint3::rfu(left, 0.0f, bottom));
    vertex.add_data3(LPoint3::rfu(right, 0.0f, top));
    vertex.add_data3(LPoint3::rfu(right, 0.0f, bottom));

    if (_bar_style.has_texture()) {
        // Generate UV's.
        PN_stdfloat left = 0.0f;
        PN_stdfloat right = get_percent() / 100.0f;
        PN_stdfloat bottom = 0.0f;
        PN_stdfloat top = 1.0f;

        GeomVertexWriter texcoord(vdata, InternalName::get_texcoord());
        texcoord.add_data2(left, top);
        texcoord.add_data2(left, bottom);
        texcoord.add_data2(right, top);
        texcoord.add_data2(right, bottom);
    }

    PT(GeomTristrips) strip = new GeomTristrips(Geom::UH_static);
    strip->add_next_vertices(4);
    strip->close_primitive();

    CPT(RenderState) state = RenderState::make(ColorAttrib::make_flat(
        _bar_style.get_color()), -1);
    if (_bar_style.has_texture()) {
        state = state->set_attrib(TextureAttrib::make(_bar_style.get_texture()));
    }
    PT(Geom) geom = new Geom(vdata);
    geom->add_primitive(strip);
    gnode->add_geom(geom, state);

    return gnode;
}

PT(PandaNode) ProgressBar::generate_texture_border_geom(const LVecBase4 &frame) {
    PT(GeomNode) gnode = new GeomNode("flat");

    PN_stdfloat left = frame[0];
    PN_stdfloat right = frame[1];
    PN_stdfloat bottom = frame[2];
    PN_stdfloat top = frame[3];

    PN_stdfloat cx = (left + right) * 0.5;
    PN_stdfloat cy = (top + bottom) * 0.5;

    LVecBase2 width = _bar_style.get_width();
    PN_stdfloat inner_left = std::min(left + width[0], cx);
    PN_stdfloat inner_right = std::max(right - width[0], cx);
    PN_stdfloat inner_bottom = std::min(bottom + width[1], cy);
    PN_stdfloat inner_top = std::max(top - width[1], cy);

    CPT(GeomVertexFormat) format;
    if (_bar_style.has_texture()) {
        format = GeomVertexFormat::get_v3t2();
    } else {
        format = GeomVertexFormat::get_v3();
    }

    PT(GeomVertexData) vdata = new GeomVertexData
        ("PGFrame", format, Geom::UH_static);

    GeomVertexWriter vertex(vdata, InternalName::get_vertex());

    // verts 0,1,2,3
    vertex.add_data3(LPoint3::rfu(left, 0.0f, top));
    vertex.add_data3(LPoint3::rfu(left, 0.0f, inner_top));
    vertex.add_data3(LPoint3::rfu(inner_left, 0.0f, top));
    vertex.add_data3(LPoint3::rfu(inner_left, 0.0f, inner_top));
    // verts 4,5,6,7
    vertex.add_data3(LPoint3::rfu(inner_right, 0.0f, top));
    vertex.add_data3(LPoint3::rfu(inner_right, 0.0f, inner_top));
    vertex.add_data3(LPoint3::rfu(right, 0.0f, top));
    vertex.add_data3(LPoint3::rfu(right, 0.0f, inner_top));
    // verts 8,9,10,11
    vertex.add_data3(LPoint3::rfu(left, 0.0f, inner_bottom));
    vertex.add_data3(LPoint3::rfu(left, 0.0f, bottom));
    vertex.add_data3(LPoint3::rfu(inner_left, 0.0f, inner_bottom));
    vertex.add_data3(LPoint3::rfu(inner_left, 0.0f, bottom));
    // verts 12,13,14,15
    vertex.add_data3(LPoint3::rfu(inner_right, 0.0f, inner_bottom));
    vertex.add_data3(LPoint3::rfu(inner_right, 0.0f, bottom));
    vertex.add_data3(LPoint3::rfu(right, 0.0f, inner_bottom));
    vertex.add_data3(LPoint3::rfu(right, 0.0f, bottom));

    if (_bar_style.has_texture()) {
        // Generate UV's.
        LVecBase2 uv_width = _bar_style.get_uv_width();
        PN_stdfloat left = 0.0f;
        PN_stdfloat right = std::max(get_percent() / 100.0f, uv_width[0]);
        PN_stdfloat bottom = 0.0f;
        PN_stdfloat top = 1.0f;

        PN_stdfloat cx = (left + right) * 0.5;
        PN_stdfloat cy = (top + bottom) * 0.5;

        PN_stdfloat inner_left = std::min(left + uv_width[0], cx);
        PN_stdfloat inner_right = std::max(right - uv_width[0], inner_left);
        PN_stdfloat inner_bottom = std::min(bottom + uv_width[1], cy);
        PN_stdfloat inner_top = std::max(top - uv_width[1], cy);

        GeomVertexWriter texcoord(vdata, InternalName::get_texcoord());

        // verts 0,1,2,3
        texcoord.add_data2(left, top);
        texcoord.add_data2(left, inner_top);
        texcoord.add_data2(inner_left, top);
        texcoord.add_data2(inner_left, inner_top);
        // verts 4,5,6,7
        texcoord.add_data2(inner_right, top);
        texcoord.add_data2(inner_right, inner_top);
        texcoord.add_data2(right, top);
        texcoord.add_data2(right, inner_top);
        // verts 8,9,10,11
        texcoord.add_data2(left, inner_bottom);
        texcoord.add_data2(left, bottom);
        texcoord.add_data2(inner_left, inner_bottom);
        texcoord.add_data2(inner_left, bottom);
        // verts 12,13,14,15
        texcoord.add_data2(inner_right, inner_bottom);
        texcoord.add_data2(inner_right, bottom);
        texcoord.add_data2(right, inner_bottom);
        texcoord.add_data2(right, bottom);
    }

    PT(GeomTristrips) strip = new GeomTristrips(Geom::UH_static);

    // tristrip #1
    strip->add_consecutive_vertices(0, 8);
    strip->close_primitive();

    // tristrip #2
    strip->add_vertex(1);
    strip->add_vertex(8);
    strip->add_vertex(3);
    strip->add_vertex(10);
    strip->add_vertex(5);
    strip->add_vertex(12);
    strip->add_vertex(7);
    strip->add_vertex(14);
    strip->close_primitive();

    // tristrip #3
    strip->add_consecutive_vertices(8, 8);
    strip->close_primitive();

    CPT(RenderState) state = RenderState::make(ColorAttrib::make_flat(
        _bar_style.get_color()), -1);
    if (_bar_style.has_texture()) {
        state = state->set_attrib(TextureAttrib::make(_bar_style.get_texture()));
    }

    PT(Geom) geom = new Geom(vdata);
    geom->add_primitive(strip);
    gnode->add_geom(geom, state);

    return gnode;
}
