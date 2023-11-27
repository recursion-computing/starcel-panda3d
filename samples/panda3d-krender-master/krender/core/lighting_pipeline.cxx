/* https://docs.microsoft.com/en-us/cpp/c-runtime-library/math-constants?view=msvc-170 */
#define _USE_MATH_DEFINES // for C
#include <math.h>

#include "camera.h"
#include "displayRegion.h"
#include "frameBufferProperties.h"
#include "geomEnums.h"
#include "pointLight.h"
#include "renderState.h"
#include "spotlight.h"
#include "texture.h"
#include "virtualFileMountRamdisk.h"
#include "virtualFileSystem.h"

#include "krender/core/lighting_pipeline.h"
#include "krender/core/helpers.h"

#ifdef CPPPARSER  // interrogate
class RPPointLight;
class RPSpotLight;

#else  // normal compiler
#include "rpPointLight.h"
#include "rpSpotLight.h"
#endif

// #define LP_DEBUG 1
#define DEPTH2COLOR 0
// #define DEPTH2COLOR 1


TypeHandle LightingPipeline::_type_handle;

LightingPipeline::LightingPipeline(
        PointerTo<GraphicsWindow> window, NodePath camera,
        bool has_srgb, bool has_pcf, unsigned int shadow_size) {
    _win = window;
    _camera = camera;
    _has_srgb = has_srgb;
    _has_pcf = has_pcf;
    _shadow_size = shadow_size;

    VirtualFileSystem* vfs = VirtualFileSystem::get_global_ptr();
    VirtualFileMountRamdisk* ramdisk = new VirtualFileMountRamdisk();
    vfs->mount(ramdisk, ".krender", 0);
    _configure();

    _scene = NodePath(new PandaNode("Scene"));
    _shadow_cams = NodePath(new PandaNode("ShadowCams"));
    _shadow_cams.reparent_to(_scene);

    _create_shadowmap();
    _create_shadow_manager();
    _create_queue();
    _create_light_manager();
    _update_shader_inputs();
}

void LightingPipeline::_configure() {
    char* config = (char*) malloc(4096 * sizeof(char));

    sprintf(
        config, "\
#define DEPTH2COLOR %d\n\
#define SUPPORTS_SHADOW_FILTER %d\n\
#define SRGB_COLOR %d\n\
#define CAM_NEAR %f\n\
#define CAM_FAR %f\n\
#define WIN_X_SIZE %d\n\
#define WIN_Y_SIZE %d\n",
        DEPTH2COLOR,
        (_win->get_gsg()->get_supports_shadow_filter() && _has_pcf) ? 1 : 0,
        (_win->get_fb_properties().get_srgb_color() && _has_srgb) ? 1 : 0,
        ((Camera*) _camera.node())->get_lens()->get_near(),
        ((Camera*) _camera.node())->get_lens()->get_far(),
        _win->get_x_size(),
        _win->get_y_size());

    VirtualFileSystem* vfs = VirtualFileSystem::get_global_ptr();
    vfs->write_file(".krender_config.inc.glsl", config, false);
    // vfs->write_file(".krender/config.inc.glsl", config, false);
    // printf("%s\n", vfs->read_file(".krender/config.inc.glsl", false).c_str());

    free(config);
}

// LightingPipeline::~LightingPipeline() {
//     free(_light_data);
// }

void LightingPipeline::_create_shadowmap() {
    _atlas_size = 256;

    // each point light containts 6 shadow sources (+X, -X, +Y, -Y, +Z, -Z)
    // defining shadow sources rows/columns
    // shadow sources are placed in a matrix:
    // rows * columns -> ss_rc * ss_rc
    int ss_rc = ceil(sqrt(MAX_LIGHTS * 6));
    while (ss_rc * _shadow_size > _atlas_size)
        _atlas_size *= 2;  // double atlas size

    FrameBufferProperties* fbp = new FrameBufferProperties();
    if (DEPTH2COLOR) {
        fbp->set_float_color(true);
        fbp->set_rgba_bits(32, 32, 32, 8);
        fbp->set_srgb_color(false);
    } else {
        fbp->set_depth_bits(32);
        fbp->set_float_depth(true);
    }

    // create FBO
    _shadowmap_fbo = _win->make_texture_buffer(
        "lighting_pipeline", _atlas_size, _atlas_size, nullptr, false, fbp);
    _shadowmap_fbo->clear_render_textures();
    _shadowmap_fbo->disable_clears();
    _shadowmap_fbo->get_overlay_display_region()->disable_clears();
    _shadowmap_fbo->get_overlay_display_region()->set_active(false);

    // remove default FBO's display regions
    _shadowmap_fbo->remove_all_display_regions();

    // also deactivate undeletable
    for (unsigned int i = 0; i < _shadowmap_fbo->get_num_display_regions(); i++) {
        DisplayRegion* region = _shadowmap_fbo->get_display_region(i);
        region->disable_clears();
        region->set_active(false);
    }

    // create shadowmap atlas texture
    _shadowmap_tex = new Texture("shadowmap");
    if (_win->get_gsg()->get_supports_shadow_filter() && _has_pcf) {
        _shadowmap_tex->set_minfilter(SamplerState::FT_shadow);
        _shadowmap_tex->set_magfilter(SamplerState::FT_shadow);
    }
    _shadowmap_fbo->add_render_texture(
        _shadowmap_tex, GraphicsOutput::RTM_bind_or_copy,
        DEPTH2COLOR ? GraphicsOutput::RTP_color : GraphicsOutput::RTP_depth);
}

void LightingPipeline::_create_shadow_manager() {
    _tag_state_manager = new TagStateManager(_camera);

    // shadow sources/atlas manager
    _shadow_manager = new ShadowManager();
    _shadow_manager->set_max_updates(MAX_UPDATES);
    _shadow_manager->set_scene(_scene);
    _shadow_manager->set_tag_state_manager(_tag_state_manager);
    _shadow_manager->set_atlas_size(_atlas_size);
    _shadow_manager->set_atlas_graphics_output(_shadowmap_fbo);
    _shadow_manager->init();

    Shader* shader = Shader::load(
        Shader::SL_GLSL,
        Filename("krender/shader/shadow.vert.glsl"),
        Filename("krender/shader/shadow.frag.glsl"));
    ConstPointerTo<RenderState> state = RenderState::make_empty();
    state = state->set_attrib(ShaderAttrib::make(shader, 200), 200);

    // reconfiture FBO's display regions
    // which was created by ShadowManager
    for (unsigned int i = 0; i < _shadowmap_fbo->get_num_display_regions(); i++) {
        DisplayRegion* region = _shadowmap_fbo->get_display_region(i);
        region->disable_clears();
        region->set_active(false);

        region->set_clear_depth_active(true);
        region->set_clear_depth(1.0);

        // reconfigure shadow caster/source camera
        // which was configured while registering camera with a TagStateManager
        NodePath camera = region->get_camera();
        if (!camera.is_empty()) {
            camera.reparent_to(_shadow_cams);
            ((Camera*) camera.node())->set_initial_state(state);
            ((Camera*) camera.node())->set_camera_mask(1 << CAMERA_BIT_SHADOW);
        }
    }
}

void LightingPipeline::_create_queue() {
    // GPU command list queue
    _gpu_command_list = new GPUCommandList();

    // GPU command data texture
    _gpu_command_data = new Texture("gpu_command_data");
    _gpu_command_data->setup_buffer_texture(
        GPU_COMMAND_SIZE * GPU_COMMAND_LIST_LIMIT,
        Texture::T_float,
        Texture::F_r32,
        GeomEnums::UH_static);
}

void LightingPipeline::_create_light_manager() {
    _light_manager = new InternalLightManager();
    _light_manager->set_shadow_update_distance(10000);
    _light_manager->set_command_list(_gpu_command_list);
    _light_manager->set_shadow_manager(_shadow_manager);

    _light_data = (LightData*) malloc(sizeof(LightData));
    memset(_light_data->data, 0, sizeof(LightData));

    _light_data_tex = new Texture("light_data");
    _light_data_tex->setup_buffer_texture(
        sizeof(_light_data->data),
        Texture::T_float,
        Texture::F_rgba32,
        GeomEnums::UH_static);
}

void LightingPipeline::_cmd_store_light(unsigned char* gpu_command_data) {
    LightPacket* light = (LightPacket*) malloc(sizeof(LightPacket));
    // read full light packet
    memcpy(light->data, gpu_command_data, sizeof(light->data));
#ifdef LP_DEBUG
    printf("CMD_store_light: ");
    print_light_packet(light);
#endif
    // store light info
    int slot = (int) light->fields.slot;
    memcpy(_light_data->contents.lights[slot].data,
           light->fields.info.data, sizeof(LightInfo));
    free(light);
}

void LightingPipeline::_cmd_remove_light(unsigned char* gpu_command_data) {
    PN_float32 slotf;
    // read light slot
    memcpy(&slotf, gpu_command_data, sizeof(slotf));
    int slot = (int) slotf;
#ifdef LP_DEBUG
    printf("CMD_remove_light: slot %d\n", slot);
#endif
    // clear light info
    memset(_light_data->contents.lights[slot].data, 0, sizeof(LightInfo));
}

void LightingPipeline::_cmd_store_source(unsigned char* gpu_command_data) {
    ShadowSourcePacket* ss = (ShadowSourcePacket*) malloc(sizeof(ShadowSourcePacket));
    // read shadow source
    memcpy(ss->data, gpu_command_data, sizeof(ss->data));
#ifdef LP_DEBUG
    printf("CMD_store_source: ");
    print_shadow_source_packet(ss);
#endif
    // store shadow source info
    int slot = (int) ss->fields.slot;
    memcpy(_light_data->contents.shadow_sources[slot].data,
           ss->fields.info.data, sizeof(ShadowSourceInfo));
    free(ss);
}

void LightingPipeline::_cmd_remove_sources(unsigned char* gpu_command_data) {
    PN_float32 slot0f;
    PN_float32 countf;
    // read first shadow source slot and count
    memcpy(&slot0f, gpu_command_data, sizeof(slot0f));
    memcpy(&countf, gpu_command_data + sizeof(slot0f), sizeof(countf));
    int slot0 = (int) slot0f;
    int count = (int) countf;
#ifdef LP_DEBUG
    printf("CMD_remove_sources: slots [%d:%d]\n", slot0, slot0 + count);
#endif
    // clear shadow sources info
    for (int i = 0; i <= count; i++) {
        memset(_light_data->contents.shadow_sources[slot0 + i].data,
               0, sizeof(ShadowSourceInfo));
    }
}

NodePath LightingPipeline::get_scene() {
    return _scene;
}

void LightingPipeline::_update_shader_inputs() {
    _scene.set_shader_input(ShaderInput(_shadowmap_tex->get_name(), _shadowmap_tex));
    _scene.set_shader_input(ShaderInput(_light_data_tex->get_name(), _light_data_tex));
    _scene.set_shader_input(ShaderInput("camera_pos", _camera.get_pos(_scene)));
}

void LightingPipeline::update() {
    _light_manager->set_camera_pos(_camera.get_pos(_scene));
    _light_manager->update();
    _shadow_manager->update();

    PTA_uchar gpu_command_data = _gpu_command_data->modify_ram_image();
    int num_commands = _gpu_command_list->write_commands_to(gpu_command_data, GPU_COMMAND_LIST_LIMIT);
    if (num_commands) {
#ifdef LP_DEBUG
        printf("GPU COMMANDS QUEUED: %d\n", num_commands);
#endif

        for (int i = 0; i < num_commands; i++) {
            int index = i * GPU_COMMAND_SIZE * R32;

            PN_float32 command;
            memcpy(&command, gpu_command_data.p()+index, sizeof(command));
            index += sizeof(command);

            switch ((int) command) {
            default:
                break;
            case GPUCommand::CMD_store_light:
                _cmd_store_light(gpu_command_data.p()+index);
                break;
            case GPUCommand::CMD_remove_light:
                _cmd_remove_light(gpu_command_data.p()+index);
                break;
            case GPUCommand::CMD_store_source:
                _cmd_store_source(gpu_command_data.p()+index);
                break;
            case GPUCommand::CMD_remove_sources:
                _cmd_remove_sources(gpu_command_data.p()+index);
                break;
            }
        }

        PTA_uchar light_data = _light_data_tex->modify_ram_image();
        memcpy(light_data.p(), _light_data->data, sizeof(_light_data->data));
    }

    _update_shader_inputs();
}

int LightingPipeline::get_num_commands() {
    return _gpu_command_list->get_num_commands();
}

int LightingPipeline::get_num_updates() {
    return MAX_UPDATES - _shadow_manager->get_num_update_slots_left();
}

void LightingPipeline::add_light(PT(RPLight) light) {
    _light_manager->add_light(light);
    _lights.push_back(light);
}

void LightingPipeline::remove_light(PT(RPLight) light) {
    for (int i = 0; i < _lights.size(); i++) {
        if (_lights[i] == light) {
            _light_manager->remove_light(light);
            _lights.erase(_lights.begin() + i);
            break;
        }
    }
}

void LightingPipeline::remove_lights() {
    for (int i = 0; i < _lights.size(); i++) {
        _light_manager->remove_light(_lights[i]);
    }
    _lights.clear();
}

int LightingPipeline::get_num_lights() {
    return _lights.size();
}

void LightingPipeline::set_shadow_update_distance(unsigned int x) {
    _light_manager->set_shadow_update_distance(x);
}

void LightingPipeline::invalidate_shadows() {
    for (int i = 0; i < _lights.size(); i++) {
        _lights[i]->invalidate_shadows();
    }
}

void LightingPipeline::prepare_scene() {
    NodePathCollection plights = _scene.find_all_matches("**/+PointLight");
    for (int i = 0; i < plights.get_num_paths(); i++) {
        NodePath light = plights.get_path(i);
        PointLight* light_node = (PointLight*) light.node();
        PT(RPPointLight) rp_light = new RPPointLight();
        rp_light->set_pos(light.get_pos(_scene));
        rp_light->set_radius(light_node->get_max_distance());
        rp_light->set_energy(20.0 * light_node->get_color().get_w());
        rp_light->set_color(light_node->get_color().get_xyz());
        rp_light->set_casts_shadows(light_node->is_shadow_caster());
        // rp_light->set_shadow_map_resolution(light_node->get_shadow_buffer_size().get_x());
        rp_light->set_shadow_map_resolution(_shadow_size);
        rp_light->set_inner_radius(0.4);
        add_light(rp_light);
    }

    NodePathCollection slights = _scene.find_all_matches("**/+Spotlight");
    for (int i = 0; i < slights.get_num_paths(); i++) {
        NodePath light = slights.get_path(i);
        Spotlight* light_node = (Spotlight*) light.node();
        PT(RPSpotLight) rp_light = new RPSpotLight();
        rp_light->set_pos(light.get_pos(_scene));
        rp_light->set_radius(light_node->get_max_distance());
        rp_light->set_energy(20.0 * light_node->get_color().get_w());
        rp_light->set_color(light_node->get_color().get_xyz());
        rp_light->set_casts_shadows(light_node->is_shadow_caster());
        // rp_light->set_shadow_map_resolution(light_node->get_shadow_buffer_size().get_x());
        rp_light->set_shadow_map_resolution(_shadow_size);
        rp_light->set_fov(light_node->get_exponent() / M_PI * 180.0);
        LVecBase3f lpoint = light.get_mat(_scene).xform_vec((0, 0, -1));
        rp_light->set_direction(lpoint);
        add_light(rp_light);
    }
}
