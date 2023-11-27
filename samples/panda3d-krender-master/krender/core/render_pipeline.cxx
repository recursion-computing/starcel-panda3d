#include "camera.h"
#include "pandaNode.h"
#include "shaderInput.h"
#include "texture.h"
#include "windowProperties.h"

#include "krender/core/helpers.h"
#include "krender/core/post_pass.h"
#include "krender/core/render_pipeline.h"
#include "krender/core/scene_pass.h"


TypeHandle RenderPipeline::_type_handle;

void RenderPipeline::add_render_pass(char* name, unsigned short type, Shader* shader) {
    RenderPass* render_pass;

    if (type == SCENE_PASS) {
        ScenePass* scene_pass = new ScenePass(
            name, _scene_passes.size(), _win, _camera, _has_srgb, _has_alpha);

        // setup camera which which captures scene
        // and renders into FBO using default camera lens
        NodePath cam = scene_pass->get_camera();
        ((Camera*) cam.node())->set_scene(get_scene());
        ((Camera*) cam.node())->set_camera_mask(
            1 << (CAMERA_BIT_DEFERRED_FIRST + _scene_passes.size()));

        _scene_passes.push_back((RenderPass*) scene_pass);

        render_pass = (RenderPass*) scene_pass;

    } else {  // POST_PASS
        // get plane from previous render pass
        NodePath prev_plane;
        if (_post_passes.size() > 0)
            prev_plane = _post_passes.back()->get_result_card();
        else
            prev_plane = _scene_passes.back()->get_result_card();

        PostPass* post_pass = new PostPass(
            name, _post_passes.size(), _win, _camera2d, _has_srgb, _has_alpha, prev_plane);

        // pass textures from the scene passes to the current render pass
        for (unsigned int i = 0; i < _scene_passes.size(); i++) {
            RenderPass* scene_pass = _scene_passes[i];
            for (unsigned int j = 0; j < scene_pass->get_num_textures(); j++) {
                PointerTo<Texture> t = scene_pass->get_texture(j);
                char* s = (char*) malloc((
                    strlen(scene_pass->get_name()) +
                    strlen(t->get_name().c_str()) + 1) * sizeof(char));
                sprintf(s, "%s_%s", scene_pass->get_name(), t->get_name().c_str());
                post_pass->get_source_card().set_shader_input(ShaderInput(std::string(s), t));
            }
        }

        // pass textures from the previous post pass to the current render pass
        RenderPass* prev_pass = NULL;
        if (_post_passes.size()) {
            prev_pass = _post_passes.back();
        } else if (_scene_passes.size()) {
            prev_pass = _scene_passes.back();
        }
        if (prev_pass != NULL) {
            for (unsigned int j = 0; j < prev_pass->get_num_textures(); j++) {
                PointerTo<Texture> t = prev_pass->get_texture(j);
                char* s = (char*) malloc((
                    strlen("prev_") + strlen(t->get_name().c_str())) * sizeof(char));
                sprintf(s, "prev_%s", t->get_name().c_str());
                post_pass->get_source_card().set_shader_input(ShaderInput(std::string(s), t));
            }
        }

        _post_passes.push_back((RenderPass*) post_pass);

        if (shader != nullptr)
            post_pass->get_source_card().set_shader(shader, 100);

        // setup projection camera which captures plane from previous render pass
        // and renders into FBO
        NodePath cam = post_pass->get_camera();
        ((Camera*) cam.node())->set_scene(prev_plane);

        render_pass = (RenderPass*) post_pass;
    }
}

NodePath RenderPipeline::get_source_card(char* name) {
    for (unsigned int i = 0; i < _scene_passes.size(); i++) {
        if (strcmp(_scene_passes[i]->get_name(), name) == 0) {
            return _scene_passes[i]->get_source_card();
        }
    }
    for (unsigned int i = 0; i < _post_passes.size(); i++) {
        if (strcmp(_post_passes[i]->get_name(), name) == 0) {
            return _post_passes[i]->get_source_card();
        }
    }
    return NodePath::not_found();
}

NodePath RenderPipeline::get_result_card(char* name) {
    for (unsigned int i = 0; i < _scene_passes.size(); i++) {
        if (strcmp(_scene_passes[i]->get_name(), name) == 0) {
            return _scene_passes[i]->get_result_card();
        }
    }
    for (unsigned int i = 0; i < _post_passes.size(); i++) {
        if (strcmp(_post_passes[i]->get_name(), name) == 0) {
            return _post_passes[i]->get_result_card();
        }
    }
    return NodePath::not_found();
}

PointerTo<Texture> RenderPipeline::get_texture(char* name, unsigned int j) {
    for (unsigned int i = 0; i < _scene_passes.size(); i++) {
        if (strcmp(_scene_passes[i]->get_name(), name) == 0) {
            return _scene_passes[i]->get_texture(j);
        }
    }
    for (unsigned int i = 0; i < _post_passes.size(); i++) {
        if (strcmp(_post_passes[i]->get_name(), name) == 0) {
            return _post_passes[i]->get_texture(j);
        }
    }
    return NULL;
}

void RenderPipeline::update() {
    if (_win_w != _win->get_x_size() || _win_h != _win->get_y_size()) {
        _win_w = _win->get_x_size();
        _win_h = _win->get_y_size();
        _configure();
        for (unsigned int i = 0; i < _scene_passes.size(); i++) {
            _scene_passes[i]->reload_shader();
        }
        for (unsigned int i = 0; i < _post_passes.size(); i++) {
            _post_passes[i]->reload_shader();
        }
    }
    LightingPipeline::update();
}
