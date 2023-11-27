#include "krender/core/scene_pass.h"


ScenePass::ScenePass(
        char* name, unsigned int index, GraphicsWindow* win, NodePath cam,
        bool has_srgb, bool has_alpha, NodePath card):
        RenderPass(name, index, win, cam, has_srgb, has_alpha, card) {
    _fbo = _make_fbo(win, has_srgb, has_alpha, 4, _index);
    _make_textures();
    char* cam_name = (char*) malloc((strlen(name) + strlen("_camera")) * sizeof(char));
    sprintf(cam_name, "%s_camera", name);
    _cam = _make_camera(_fbo, cam_name, cam);
}

void ScenePass::_make_textures() {
    RenderPass::_make_textures();

    char* tex_name;
    PointerTo<Texture> t;

    t = new Texture("depth");
    t->set_format(Texture::Format::F_depth_component);
    t->set_wrap_u(SamplerState::WM_clamp);
    t->set_wrap_v(SamplerState::WM_clamp);
    t->set_magfilter(SamplerState::FilterType::FT_linear);
    t->set_minfilter(SamplerState::FilterType::FT_linear);
    _fbo->add_render_texture(t, GraphicsOutput::RTM_bind_or_copy, GraphicsOutput::RTP_depth);
    _tex.push_back(t);

    t = new Texture("emissive");
    t->set_format(Texture::Format::F_srgb_alpha);
    t->set_wrap_u(SamplerState::WM_clamp);
    t->set_wrap_v(SamplerState::WM_clamp);
    t->set_magfilter(SamplerState::FilterType::FT_linear);
    t->set_minfilter(SamplerState::FilterType::FT_linear);
    _fbo->add_render_texture(t, GraphicsOutput::RTM_bind_or_copy, GraphicsOutput::RTP_aux_rgba_0);
    _tex.push_back(t);

    t = new Texture("selector");
    t->set_format(Texture::Format::F_srgb_alpha);
    t->set_wrap_u(SamplerState::WM_clamp);
    t->set_wrap_v(SamplerState::WM_clamp);
    t->set_magfilter(SamplerState::FilterType::FT_linear);
    t->set_minfilter(SamplerState::FilterType::FT_linear);
    _fbo->add_render_texture(t, GraphicsOutput::RTM_bind_or_copy, GraphicsOutput::RTP_aux_rgba_1);
    _tex.push_back(t);
}

/*
 * Makes a new 3D camera, ShowBase's makeCamera reimplementation.
 */
NodePath ScenePass::_make_camera(PointerTo<GraphicsOutput> fbo, char* name, NodePath camera) {
    NodePath cam = camera.attach_new_node(new Camera(name));

    ((Camera*) cam.node())->set_lens(((Camera*) camera.node())->get_lens());

    DisplayRegion* dr = fbo->make_display_region();
    dr->set_sort(_index);
    dr->set_camera(cam);

    return cam;
}
