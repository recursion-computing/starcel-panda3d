from direct.task.Task import Task
from client.local.section.main.scene.actor_manipulation.unit_interpolator import (
    UnitInterpolator,
)
from client.local.section.main.scene.actor_manipulation.anim_mgr import AnimationManager
from client.local import core
from client.event import Event
from direct.showbase.DirectObject import DirectObject
from client.local.model.unit_model_bank import UnitModelBank
from client.local.model.weapon_model_bank import WeaponModelBank
from client.local.animation.bank import AnimationBank


class ActorManipulator(DirectObject):
    def __init__(self, model, node):
        DirectObject.__init__(self)
        self.model = model
        self.node = node

        self.accept(Event.NEW_UNIT_CREATED, self.handle_new_unit_created)
        self.accept(Event.UNIT_ANIMATION_UPDATED, self.handle_unit_animation_updated)
        self.accept(Event.UNIT_MODEL_UPDATED, self.handle_unit_model_updated)
        self.accept(Event.UNIT_WEAPON_UPDATED, self.handle_weapon_changed)
        self.accept(Event.UNIT_SCALE_UPDATED, self.handle_unit_scale_updated)

    def handle_unit_scale_updated(self, *args):
        unit = args[0]
        unit.base_node.set_scale(unit.scale)

    def handle_new_unit_created(self, *args):
        unit = args[0]
        self.spawn_unit(unit)

    def handle_unit_animation_updated(self, *args):
        unit, loop = args
        self.change_animation(unit, unit.animation_str, loop)

    def handle_unit_model_updated(self, *args):
        unit = args[0]
        unit.actor.removePart("modelRoot")
        unit.actor = UnitModelBank.get_by_id(unit.model_id)()
        unit.anim_mgr = AnimationManager(unit.actor)
        unit.actor.reparent_to(unit.base_node)
        self.change_animation(unit, unit.animation_str, 0)
        weapon = WeaponModelBank.get_by_id(unit.weapon_id)()
        self.equip_weapon(unit, weapon)

    def handle_weapon_changed(self, *args):
        unit, = args
        self.change_weapon(unit, unit.weapon_id)
        # weapon = WeaponModelBank.get_by_id(unit.weapon_id)()
        # self.equip_weapon(unit, weapon)

    def spawn_unit(self, unit):
        unit.actor = UnitModelBank.get_by_id(unit.model_id)()
        unit.anim_mgr = AnimationManager(unit.actor)
        weapon = WeaponModelBank.get_by_id(unit.weapon_id)()
        self.equip_weapon(unit, weapon)
        self.change_animation(unit, unit.animation_str, 1)
        unit.base_node = self.node.attach_new_node("actor base node")
        unit.base_node.set_scale(unit.scale)
        unit.base_node.set_pos_hpr(unit.x, unit.y, unit.z, unit.h, unit.p, unit.r)
        unit.actor.reparent_to(unit.base_node)
        unit.actor.set_blend(frameBlend=True)
        if unit != self.model.player_unit:
            unit.interpolator = UnitInterpolator(unit)
            unit.interpolator.update()
            task = Task(self.update_position_task)
            core.instance.task_mgr.add(
                task, f"interpolate{unit}", extraArgs=[unit, task]
            )

    def move_rotate_character(self, unit, x, y, z, h, p, r):
        unit.base_node.set_pos_hpr(x, y, z, h, p, r)

    def change_animation(self, unit, animation, loop):
        unit.anim_mgr.consider_animation(AnimationBank.get_animation_by_string(animation))

    def equip_weapon(self, unit, weapon):
        unit.hand_node = unit.actor.expose_joint(None, "modelRoot", "Weapon_R_Bone")
        weapon.reparent_to(unit.hand_node)
        unit.weapon_node = weapon

    def change_weapon(self, unit, weapon):
        unit.weapon_node.detach_node()
        unit.weapon_node = WeaponModelBank.get_by_id(unit.weapon_id)()
        unit.weapon_node.reparent_to(unit.hand_node)

    def update_position_task(self, unit, task):
        unit.interpolator.interpolate()
        return Task.cont
