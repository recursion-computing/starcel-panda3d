from client.local import core
from client.local.font import MainFont
from client.event import Event

from random import uniform

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectLabel
from direct.task.Task import Task
from panda3d.core import Vec3


class DmgText(DirectObject):
    """
    We multiply displayed damage for "cooler" effect.
    """

    def __init__(self, model):
        DirectObject.__init__(self)
        self.model = model
        self.accept(Event.COMBAT_DATA_PARSED, self.handle_combat_data_parsed)

        # shaking text settings
        self.init_displacement = 0.2
        self.shake_strength = 0.02
        self.scale_factor = 0.5
        self.floating_up_speed = 0.02
        # XD depending on this value, the scale & trembling is adjusted
        self.big_dmg_assumption = 50

    def handle_combat_data_parsed(self, *args):
        hp_change = args[1]
        targets_ids = args[3]
        this_player_is_source = args[4]
        this_player_is_target = args[5]

        if this_player_is_target:
            color = (204, 0, 0, 1)
            self.create_randomly_placed_text(self.model.player_unit.base_node, hp_change, color)
            return

        elif this_player_is_source:
            color = (204, 204, 0, 1)
            for target_id in targets_ids:
                unit = self.model.units_by_id.get(target_id, None)
                if unit is not None:
                    self.create_randomly_placed_text(unit.base_node, hp_change, color)

    def create_randomly_placed_text(self, node, value, color):
        font = MainFont()
        text_node = node.attach_new_node("text node")
        text_node.set_pos(
            uniform(-self.init_displacement, self.init_displacement),
            0,
            uniform(self.init_displacement, self.init_displacement),
        )

        scale = 0.15

        text = DirectLabel(
            text=str(value),
            scale=scale,
            parent=text_node,
            text_bg=(0, 0, 0, 0),
            text_fg=color,
            frameColor=(0, 0, 0, 0),
            text_font=font,
        )
        text.set_compass(core.instance.camera)
        task = Task(self.shake_and_fade_out_text, "fade out text")
        time = 3
        strength = scale * 0.01
        core.instance.task_mgr.add(
            task, extraArgs=[task, text, text_node, time, strength, color]
        )

    def shake_and_fade_out_text(self, task, text, text_node, time, strength, start_color):
        if task.time < time:
            text_node.set_pos(
                text_node,
                Vec3(
                    uniform(-strength, strength),
                    0,
                    uniform(-strength, strength),
                ),
            )
            text["text_fg"] = (204, 204, 0, 1 - task.time / time)
            text_node.set_z(text_node, self.floating_up_speed)
            text_node.set_pos(
                text_node,
                Vec3(
                    uniform(-strength, strength),
                    0,
                    uniform(-strength, strength),
                ),
            )
            text["text_fg"] = (start_color[0], start_color[1], start_color[2], start_color[3] - task.time / time)
            return Task.cont
        else:
            self.destroy_text(text_node)
            return Task.done

    def destroy_text(self, text):
        text.remove_node()
