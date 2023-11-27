#include "krender/core/post_pass.h"

#include "lens.h"
#include "orthographicLens.h"


PostPass::PostPass(
        char* name, unsigned int index, GraphicsWindow* win, NodePath cam,
        bool has_srgb, bool has_alpha, NodePath card):
        RenderPass(name, index, win, cam, has_srgb, has_alpha, card) {
    _fbo = _make_fbo(win, has_srgb, has_alpha, 1, _index + 10);
    _make_textures();
    char* cam_name = (char*) malloc((strlen(name) + strlen("_camera")) * sizeof(char));
    sprintf(cam_name, "%s_camera", name);
    _cam = _make_camera(_fbo, cam_name, cam);
}

/*
 * Makes a new 2D camera, ShowBase's makeCamera2d reimplementation.
 */
NodePath PostPass::_make_camera(PointerTo<GraphicsOutput> fbo, char* name, NodePath camera2d) {
    NodePath cam = camera2d.attach_new_node(new Camera(name));

    const int left = -1;
    const int right = 1;
    const int bottom = -1;
    const int top = 1;
    Lens* lens = new OrthographicLens();
    lens->set_film_size(right - left, top - bottom);
    lens->set_film_offset((right + left) * 0.5, (top + bottom) * 0.5);
    lens->set_near_far(-1000, 1000);
    ((Camera*) cam.node())->set_lens(lens);

    DisplayRegion* dr = fbo->make_mono_display_region();
    dr->set_clear_depth_active(1);
    dr->set_incomplete_render(false);
    dr->set_sort(_index + 10);
    dr->set_camera(cam);

    return cam;
}
