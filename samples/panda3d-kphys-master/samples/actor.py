#!/usr/bin/env python3
import os
import sys

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_PATH, 'dist'))

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText

from panda3d.core import load_prc_file_data, NodePath, Shader, TextNode

from kphys.core import EffectorNode, IK_ENGINE_IK, IK_ENGINE_CCDIK
from kphys.loader import load_actor

from common import make_empty


class ActorSample(ShowBase):
    def __init__(self):
        load_prc_file_data('', '''
            framebuffer-alpha f
            win-size 1280 720
        ''')

        ShowBase.__init__(self)

        self.cam.set_y(-4)
        self.cam.set_z(0.7)

        self._actors = []
        self._effectors = {
            'top': [],
            'left': [],
            'right': [],
        }
        self._texts = []
        for i in range(2):
            filepath = os.path.join(os.path.dirname(__file__), 'yuki', 'scene.gltf')
            node = load_actor(filepath)
            scene = NodePath(node)
            actor = scene.find('**/+ArmatureNode')
            actor.reparent_to(self.render)
            actor.set_x(i - 0.5)
            actor.node().update_shader_inputs()

            bone = actor.find('**/mixamorig:Head_06')
            effector = NodePath(EffectorNode('Effector Head', chain_length=4, priority=0))
            effector.reparent_to(bone)
            self._effectors['top'].append(effector)

            bone = actor.find('**/mixamorig:LeftHand_011')
            effector = NodePath(EffectorNode('Effector Hand_L', chain_length=2, priority=1))
            effector.reparent_to(bone)
            self._effectors['left'].append(effector)

            bone = actor.find('**/mixamorig:RightHand_026')
            effector = NodePath(EffectorNode('Effector Hand_R', chain_length=2, priority=1))
            effector.reparent_to(bone)
            self._effectors['right'].append(effector)

            actor.ls()
            for bone in actor.find_all_matches('**/+BoneNode'):
                make_empty(parent=bone)
            for bone in actor.find_all_matches('**/+EffectorNode'):
                make_empty(parent=bone)

            actor.node().rebuild_bind_pose()
            if i == 0:
                actor.node().rebuild_ik(IK_ENGINE_IK)
                text = OnscreenText(
                    text='FABRIK', pos=(i - 0.5, 0.75), align=TextNode.ACenter,
                    parent=self.render2d)
                self._texts.append(text)
            else:
                actor.node().rebuild_ik(IK_ENGINE_CCDIK)
                text = OnscreenText(
                    text='CCD', pos=(i - 0.5, 0.75), align=TextNode.ACenter,
                    parent=self.render2d)
                self._texts.append(text)

            self._actors.append(actor)

            shader_parts = {}
            for stype in ('fragment', 'vertex'):
                ftype = stype[:4]
                filepath = os.path.join(os.path.dirname(__file__), f'actor.{ftype}.glsl')
                with open(filepath, 'r') as f:
                    shader_parts[stype] = f.read()
            shader = Shader.make(Shader.SL_GLSL, **shader_parts)
            for geom in actor.find_all_matches('**/+GeomNode'):
                if geom.get_name() != 'lineNode':  # don't apply skinning to axis lines
                    geom.set_shader(shader)

        self.accept('f3', self.toggleWireframe)
        self.accept('escape', sys.exit)
        self.accept('q', sys.exit)
        self.accept('l', self._actors_ls)
        self.accept('r', self._actors_reset)
        self.task_mgr.add(self._update, '_update')

        for k in (tuple('wasduhjk') + ('arrow_left', 'arrow_right', 'arrow_up', 'arrow_down')):
            self.accept(k, self._set_key, [k, True])
            self.accept(f'{k}-up', self._set_key, [k, False])

        self._keymap = {}

    def _set_key(self, key, value):
        self._keymap[key] = value

    def _actors_ls(self):
        for actor in self._actors:
            actor.ls()

    def _actors_reset(self):
        for actor in self._actors:
            actor.node().reset()

    def _move_effectors(self, etype, direction, delta):
        for effector in self._effectors[etype]:
            getter = getattr(effector, f'get_{direction}')
            setter = getattr(effector, f'set_{direction}')
            value = getter(self.render)
            setter(self.render, value + delta)

    def _update(self, task):
        dt = self.clock.dt

        if self._keymap.get('arrow_left'):
            self._move_effectors('top', 'x', -dt)
        if self._keymap.get('arrow_right'):
            self._move_effectors('top', 'x', dt)
        if self._keymap.get('arrow_up'):
            self._move_effectors('top', 'z', dt)
        if self._keymap.get('arrow_down'):
            self._move_effectors('top', 'z', -dt)

        if self._keymap.get('a'):
            self._move_effectors('left', 'x', -dt)
        if self._keymap.get('d'):
            self._move_effectors('left', 'x', dt)
        if self._keymap.get('w'):
            self._move_effectors('left', 'z', dt)
        if self._keymap.get('s'):
            self._move_effectors('left', 'z', -dt)

        if self._keymap.get('h'):
            self._move_effectors('right', 'x', -dt)
        if self._keymap.get('k'):
            self._move_effectors('right', 'x', dt)
        if self._keymap.get('u'):
            self._move_effectors('right', 'z', dt)
        if self._keymap.get('j'):
            self._move_effectors('right', 'z', -dt)

        for actor in self._actors:
            actor.node().reset()
            actor.node().update_ik()
            actor.node().update_shader_inputs()

        return task.again


sample = ActorSample()
sample.run()
