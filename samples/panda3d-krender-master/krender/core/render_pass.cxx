#include <stdlib.h>
#include <string.h>

#include "displayRegion.h"
#include "frameBufferProperties.h"
#include "graphicsWindow.h"
#include "pandaNode.h"
#include "texture.h"
#include "transformState.h"
#include "windowProperties.h"

#include "krender/core/render_pass.h"


RenderPass::RenderPass(char* name, unsigned int index, GraphicsWindow* win, NodePath cam,
                       bool has_srgb, bool has_alpha, NodePath card) {
    _name = name;
    _index = index;
    _source_card = card;
}

char* RenderPass::get_name() {
    return _name;
}

NodePath RenderPass::get_camera() {
    return _cam;
}

NodePath RenderPass::get_source_card() {
    return _source_card;
}

NodePath RenderPass::get_result_card() {
    return _result_card;
}

PointerTo<Texture> RenderPass::get_texture(unsigned int i) {
    return _tex[i];
}

unsigned int RenderPass::get_num_textures() {
    return _tex.size();
}

void RenderPass::reload_shader() {
    if (_source_card.is_empty())
        return;

    const Shader* shaderc = _source_card.get_shader();
    if (shaderc == nullptr)
        return;

    Filename vert = shaderc->get_filename(Shader::ST_vertex).get_fullpath();
    Filename frag = shaderc->get_filename(Shader::ST_fragment).get_fullpath();

    Shader* shader = Shader::load(Shader::SL_GLSL, vert, frag);
    _source_card.clear_shader();
    _source_card.set_shader(shader, 100);
}

PointerTo<GraphicsOutput> RenderPass::_make_fbo(
        PointerTo<GraphicsWindow> win, bool has_srgb, bool has_alpha,
        unsigned short num_textures, unsigned short sort) {
    FrameBufferProperties* fbp = new FrameBufferProperties();
    fbp->set_rgba_bits(1, 1, 1, 1);
    if (has_srgb)
        fbp->set_srgb_color(true);
    if (num_textures > 1) {
        fbp->set_depth_bits(32);
        fbp->set_float_depth(true);
        fbp->set_aux_rgba(2);
    }

    PointerTo<GraphicsOutput> fbo = win->make_texture_buffer(_name, 0, 0, nullptr, false, fbp);
    fbo->clear_render_textures();
    fbo->set_sort(sort - 10);
    if (has_alpha)
        fbo->set_clear_color(LVecBase4(0, 0, 0, 0));
    else
        fbo->set_clear_color(LVecBase4(0, 0, 0, 1));

    char* card_name = (char*) malloc((strlen(_name) + strlen("_card")) * sizeof(char));
    sprintf(card_name, "%s_card", _name);

    _result_card = fbo->get_texture_card();
    _result_card.set_name(card_name);

    return fbo;
}

void RenderPass::_make_textures() {
    char* tex_name;
    PointerTo<Texture> t;

    t = new Texture("color");
    t->set_format(Texture::Format::F_srgb_alpha);
    t->set_wrap_u(SamplerState::WM_clamp);
    t->set_wrap_v(SamplerState::WM_clamp);
    t->set_magfilter(SamplerState::FilterType::FT_linear);
    t->set_minfilter(SamplerState::FilterType::FT_linear);
    _fbo->add_render_texture(t, GraphicsOutput::RTM_bind_or_copy, GraphicsOutput::RTP_color);
    _tex.push_back(t);
}
