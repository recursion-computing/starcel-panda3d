#!/usr/bin/env python3
import os
import sys

# PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, os.path.join(PROJECT_PATH, 'dist'))

from krender.core import RenderPipeline

from direct.gui.DirectGui import OnscreenImage
from direct.showbase.ShowBase import ShowBase

from panda3d.core import (
    get_model_path, load_prc_file_data, ClockObject, LColor,
    Material, NodePath, PointLight, Shader, Texture)


class Sample(ShowBase):
    def __init__(self):
        load_prc_file_data('', '''
            win-size 1280 720
            framebuffer-srgb t
            framebuffer-alpha f
            show-frame-rate-meter t
            textures-power-2 f
        ''')
        super().__init__()
        has_srgb = self.win.get_fb_properties().get_srgb_color()

        # add krender module to search path
        from krender import core
        get_model_path().prepend_directory(os.path.dirname(os.path.dirname(core.__file__)))

        # limit to 60 FPS
        clock = ClockObject.get_global_clock()
        clock.set_mode(ClockObject.MLimited)
        clock.set_frame_rate(60)

        # create pipeline with default initial render pass
        self._render_pipeline = RenderPipeline(
            self.win, self.render2d, self.cam, self.cam2d,
            has_srgb=has_srgb, has_alpha=False, has_pcf=True, shadow_size=512)
        self._render_pipeline.add_render_pass('base', 0)

        # add depth of field render pass
        self._render_pipeline.add_render_pass('dof', 1)
        dof_card = self._render_pipeline.get_source_card('dof')
        dof_card.set_shader_input('dof_focus_near', 15.0)
        dof_card.set_shader_input('dof_blur_near', 15.0 - 5.0)
        dof_card.set_shader_input('dof_focus_far', 20.0)
        dof_card.set_shader_input('dof_blur_far', 20.0 + 5.0)
        dof_card.set_shader(Shader.load(
            Shader.SL_GLSL,
            'krender/shader/dof.vert.glsl',
            'krender/shader/dof.frag.glsl'), 100)

        # add bloom render pass
        self._render_pipeline.add_render_pass('bloom', 1, Shader.load(
            Shader.SL_GLSL,
            'krender/shader/bloom.vert.glsl',
            'krender/shader/bloom.frag.glsl'))

        # prepare scene with default shaders
        scene = self._render_pipeline.get_scene()
        scene.set_shader(Shader.load(
            Shader.SL_GLSL,
            'krender/shader/default.vert.glsl',
            'krender/shader/default.frag.glsl'), 100)

        # show last pass on screen
        tex = self._render_pipeline.get_texture('bloom', 0)
        self._viewer = OnscreenImage(parent=self.render2d)
        self._viewer.setImage(tex)
        self._viewer.reparent_to(self.render2d)

        # move camera
        self.cam.set_pos(-2.5, -20, 1.5)

        # load environment
        room = self.loader.load_model('room_industrial.egg.pz')
        room.reparent_to(scene)
        room.set_scale(0.5)

        # load monkey and make it emissive
        monkey = self.loader.load_model('monkey.egg.pz')
        monkey.set_scale(0.5)
        monkey.set_pos(-2.5, -4, 2)
        monkey.reparent_to(scene)
        monkey.hide(1 << 1)  # hide from shadowmapper's cameras, so it doesn't drop shadows
        material = Material()
        material.set_base_color(LColor(0, 1, 0, 0))
        material.set_emission(LColor(0, 1, 0, 0))
        monkey.set_material(material)

        # load movable entity
        self._entity = self.loader.load_model('crate.egg.pz')
        self._entity.reparent_to(scene)

        # force textures to use sRGB
        for t in scene.find_all_textures():
            if t.get_format() == Texture.F_rgb:
                t.set_format(Texture.F_srgb)
            if t.get_format() == Texture.F_rgba:
                t.set_format(Texture.F_srgb_alpha)

        # add light
        light = NodePath(PointLight('Point'))
        light.node().set_color(LColor(1, 0.4, 0.4, 3))
        # light.node().show_frustum()
        light.node().set_shadow_caster(True)
        light.node().set_max_distance(10)
        light.set_pos(0, -6, 2)
        light.reparent_to(scene)

        # add another light
        light = NodePath(PointLight('Point.001'))
        light.node().set_color(LColor(0.4, 0.4, 1, 3))
        # light.node().show_frustum()
        light.node().set_shadow_caster(True)
        light.node().set_max_distance(10)
        light.set_pos(-5, -6, 2)
        light.reparent_to(scene)

        # create RP compatible lights from panda's lights
        self._render_pipeline.prepare_scene()

        # generic key bingins
        self.accept('escape', sys.exit)
        self.accept('q', sys.exit)
        self.accept('f3', self.toggleWireframe)
        self.accept('f4', self.bufferViewer.toggleEnable)
        self.accept('f5', self._render_pipeline.invalidate_shadows)

        # entity movement keys
        self._movement = {}
        self.accept('w', lambda: self._move('up', True))
        self.accept('w-up', lambda: self._move('up', False))
        self.accept('s', lambda: self._move('down', True))
        self.accept('s-up', lambda: self._move('down', False))
        self.accept('a', lambda: self._move('left', True))
        self.accept('a-up', lambda: self._move('left', False))
        self.accept('d', lambda: self._move('right', True))
        self.accept('d-up', lambda: self._move('right', False))

        # main game loop
        self.task_mgr.add(self.update, 'update')

    def _move(self, side, active):
        self._movement[side] = active

    def update(self, task):
        dt = ClockObject.get_global_clock().get_dt()
        speed = 5

        # move entity
        if self._movement.get('up') and not self._movement.get('down'):
            self._entity.set_y(self._entity, dt * speed)
        elif not self._movement.get('up') and self._movement.get('down'):
            self._entity.set_y(self._entity, dt * -speed)
        if self._movement.get('left') and not self._movement.get('right'):
            self._entity.set_x(self._entity, dt * -speed)
        elif not self._movement.get('left') and self._movement.get('right'):
            self._entity.set_x(self._entity, dt * speed)

        ncmd = self._render_pipeline.get_num_commands()
        if ncmd:
            print('COMMANDS', ncmd)

        nupd = self._render_pipeline.get_num_updates()
        if nupd:
            print('UPDATES', nupd)

        # execute queued commands
        self._render_pipeline.update()

        # force shadows to be rendered into shadowmap atlas again
        self._render_pipeline.invalidate_shadows()

        return task.again


app = Sample()
app.run()
