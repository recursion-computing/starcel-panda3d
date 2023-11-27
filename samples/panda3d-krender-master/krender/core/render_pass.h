#ifndef CORE_RENDER_PASS_H
#define CORE_RENDER_PASS_H

#include "graphicsOutput.h"
#include "graphicsWindow.h"
#include "nodePath.h"
#include "texture.h"
#include "pvector.h"

BEGIN_PUBLISH
enum RenderPassType {
    SCENE_PASS = 0,
    POST_PASS = 1
};
END_PUBLISH


class RenderPass {
public:
    RenderPass(
        char* name, unsigned int index, GraphicsWindow* win, NodePath cam,
        bool has_srgb=false, bool has_alpha=false,
        NodePath card=NodePath::not_found());
    char* get_name();
    NodePath get_camera();
    NodePath get_source_card();
    NodePath get_result_card();
    PointerTo<Texture> get_texture(unsigned int i);
    unsigned int get_num_textures();
    void reload_shader();

protected:
    char* _name;
    unsigned int _index;
    PointerTo<GraphicsOutput> _fbo;
    pvector<PointerTo<Texture>> _tex;
    NodePath _cam;
    NodePath _source_card;
    NodePath _result_card;

    PointerTo<GraphicsOutput> _make_fbo(
        PointerTo<GraphicsWindow> win, bool has_srgb=false, bool has_alpha=false,
        unsigned short num_textures=1, unsigned short sort=0);
    void _make_textures();
};

#endif
