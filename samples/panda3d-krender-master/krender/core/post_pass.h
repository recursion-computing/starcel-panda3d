#ifndef CORE_POST_PASS_H
#define CORE_POST_PASS_H

#include "krender/core/render_pass.h"


class PostPass: public RenderPass {
public:
    PostPass(
        char* name, unsigned int index, GraphicsWindow* win, NodePath cam,
        bool has_srgb=false, bool has_alpha=false, NodePath card=NodePath::not_found());

private:
    NodePath _make_camera(PointerTo<GraphicsOutput> fbo, char* name, NodePath camera);
};

#endif
