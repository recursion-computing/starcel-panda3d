#ifndef CORE_RENDER_PIPELINE_H
#define CORE_RENDER_PIPELINE_H

#include "graphicsWindow.h"
#include "nodePath.h"
#include "pandabase.h"
#include "pvector.h"
#include "typedWritableReferenceCount.h"

#include "krender/core/render_pass.h"
#include "krender/core/lighting_pipeline.h"


class EXPORT_CLASS RenderPipeline: public LightingPipeline {
PUBLISHED:
    RenderPipeline(
            GraphicsWindow* window, NodePath render2d, NodePath camera, NodePath camera2d,
            unsigned int shadow_size=512,
            bool has_srgb=false, bool has_pcf=false, bool has_alpha=false):
    LightingPipeline(window, camera, has_srgb, has_pcf, shadow_size) {
        _camera2d = camera2d;
        _render2d = render2d;
        _has_alpha = has_alpha;
        _win_w = window->get_x_size();
        _win_h = window->get_y_size();
    };
    void add_render_pass(char* name, unsigned short type, Shader* shader=nullptr);
    NodePath get_source_card(char* name);
    NodePath get_result_card(char* name);
    PointerTo<Texture> get_texture(char* name, unsigned int i);
    void update();

private:
    NodePath _camera2d;
    NodePath _render2d;
    bool _has_alpha;
    unsigned int _win_w;
    unsigned int _win_h;

    int _index;
    pvector<RenderPass*> _scene_passes;
    pvector<RenderPass*> _post_passes;
    static TypeHandle _type_handle;

public:
    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        LightingPipeline::init_type();
        register_type(
            _type_handle, "RenderPipeline",
            TypedWritableReferenceCount::get_class_type());
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
