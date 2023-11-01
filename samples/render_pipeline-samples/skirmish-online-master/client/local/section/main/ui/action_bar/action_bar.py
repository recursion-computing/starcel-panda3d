from client.local import core
from client.event import Event
from direct.showbase.DirectObject import DirectObject
from ..utils.frame import Frame
from .cooldown_trackers import TrackerSpell1, TrackerSpell2, TrackerSpell3, TrackerSpell4
from .slot import SpellSlot
from direct.task.Task import Task


class ActionBar(DirectObject):
    """
    GUI element responsible for displaying available spells and their cooldowns.
    """
    N_SLOTS = 9

    def __init__(self, parent_node, y=0):
        DirectObject.__init__(self)
        self.accept(Event.COMBAT_DATA_PARSED, self.handle_combat_data_parsed)
        self.node = parent_node.attach_new_node("action bar")
        self.frame = Frame(parent_node=self.node,
                           color=(0, 0, 0, 0.6),
                           x=0,
                           y=0.01,
                           width=0.25,
                           height=0.047)
        self.y = y
        x_offset = 0.026
        spell_slot_width = 0.025
        padding = 0.003
        y_offset = 0.057
        self.spell_slots = []
        tracker_classes = [TrackerSpell1, TrackerSpell2, TrackerSpell3, TrackerSpell4]
        for i in range(self.N_SLOTS):
            if i in range(0, len(tracker_classes)):
                tracker_cls = tracker_classes[i]
            else:
                tracker_cls = None

            slot = SpellSlot(
                node=self.node,
                tracker_cls=tracker_cls,
                x_offset=x_offset,
                y_offset=y_offset,
                parent_frame=None
             )
            self.spell_slots.append(slot)
            # self.set_cooldown_tracking()
            x_offset += spell_slot_width + padding

        self.accept("aspectRatioChanged", self.aspect_ratio_change_update)

    def get_window_size(self):
        return core.instance.win.get_x_size(), core.instance.win.get_y_size()

    def aspect_ratio_change_update(self):
        ww, wh = self.get_window_size()
        self.update_position(ww, wh)

    def update_position(self, ww, wh):
        ww, wh = self.get_window_size()
        frame_width_px = self.frame.width * ww
        y_offset_px = self.y * wh
        x_px = ww / 2 - frame_width_px / 2
        y_px = - wh + y_offset_px
        self.node.set_pos(x_px, 0, y_px)

    def handle_combat_data_parsed(self, *args):
        spell_id = args[0]
        hp_change = args[1]
        this_player_is_source = args[4]

        if not this_player_is_source or hp_change == 0:
            return

        slot = self.spell_slots[spell_id]

        # trigger cooldown for the spell
        task = Task(slot.update_cooldown_view, "update cooldown view")
        core.instance.task_mgr.add(task, extraArgs=[task, slot.tracker_cls.DEFAULT_COOLDOWN])

        # trigger global cooldown
        # so that spells aren't used more often than 1 second
        for i, slot in enumerate(self.spell_slots):
            if i != spell_id and slot.tracker_cls is not None:
                if slot.remaining_time < 1:
                    task = Task(slot.update_cooldown_view, "update cooldown view")
                    slot.remaining_time = 1
                    slot.temp_cooldown = 1
                    core.instance.task_mgr.add(task, extraArgs=[task, slot.temp_cooldown])





