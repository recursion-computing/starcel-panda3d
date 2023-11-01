from direct.showbase.DirectObject import DirectObject
from client.local.section.main.ui.utils.frame import Frame
from client.local.section.main.ui.utils.wait_bar import WaitBar
from direct.task.Task import Task
from client.local import core


class SpellSlot(DirectObject):
    def __init__(self, tracker_cls, node, x_offset, y_offset, parent_frame=None):
        DirectObject.__init__(self)
        self.node = node.attach_new_node("action bar")
        self.tracker_cls = tracker_cls
        if tracker_cls is None:
            color = (0, 0, 0, 1)
            icon = None
            text = ""
        else:
            color = (1, 1, 1, 1)
            icon = tracker_cls.ICON
            text = tracker_cls.DISPLAYED_TEXT

        self.frame = Frame(parent_node=self.node,
                           color=color,
                           x=x_offset,
                           y=y_offset,
                           width=0.026,
                           height=0.046,
                           hpr=(0, 0, 180),
                           image=icon,
                           text=text,
                           )

        if tracker_cls is not None:
            self.cd_bar = WaitBar(parent=self.frame.node)
            self.remaining_time = tracker_cls.DEFAULT_COOLDOWN
            self.temp_cooldown = tracker_cls.DEFAULT_COOLDOWN
            self.update_view(self.remaining_time, self.temp_cooldown)
            self.accept(self.tracker_cls.KEY_EVENT, self.handle_spell_key_pressed)
            self.accept(f"{self.tracker_cls.KEY_EVENT}-up", self.handle_spell_key_released)
            # trigger cooldown for the spell
            task = Task(self.update_cooldown_view, "update cooldown view")
            core.instance.task_mgr.add(task, extraArgs=[task, self.tracker_cls.DEFAULT_COOLDOWN])

        self.accept("aspectRatioChanged", self.aspect_ratio_change_update)

    def aspect_ratio_change_update(self):
        if self.tracker_cls is not None:
            self.update_view(self.remaining_time, self.temp_cooldown)

    def update_cooldown_view(self, task, cooldown):
        remaining_time = cooldown - task.time
        if remaining_time > 0:
            self.remaining_time = remaining_time
            self.update_view(remaining_time, cooldown)
            return Task.cont
        else:
            self.remaining_time = 0
            return Task.done

    def update_view(self, remaining_time, cooldown):
        cooldown_elapsed_percent = 1 - remaining_time / cooldown
        self.cd_bar.wait_bar["barColor"] = (1 - cooldown_elapsed_percent, cooldown_elapsed_percent, 0, 1)
        self.cd_bar.wait_bar["value"] = cooldown_elapsed_percent * 100

    def handle_spell_key_pressed(self):
        self.frame.frame["frameColor"] = (1, 1, 1, 0.5)

    def handle_spell_key_released(self):
        self.frame.frame["frameColor"] = (1, 1, 1, 1)


