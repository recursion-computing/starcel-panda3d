from client.local import core
from client.local.font import MainFont
from client.event import Event

from ..model.model import MainSectionModel

from direct.gui.DirectGui import DirectWaitBar, DirectLabel, DirectFrame
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task

from datetime import datetime, timedelta


class ChatBubbles(DirectObject):
    def __init__(self, model: MainSectionModel):
        DirectObject.__init__(self)
        self.model = model
        self.chat_bubbles_by_names = {}
        self.seconds_per_bubble = 5 # seconds
        self.accept(Event.MSG_RECEIVED, self.handle_msg_received)
        self.accept(Event.UNIT_DISCONNECTED, self.handle_unit_disconnected)

    def handle_msg_received(self, *args):
        name, time, msg = args
        unit = self.model.get_unit_by_name(name)
        if unit is not None:
            self.recreate_bubble(unit, msg)

    def handle_unit_disconnected(self, *args):
        unit_id = args[0]
        unit = self.model.units_by_id.get(unit_id, None)
        if unit is not None:
            self.remove_existing_bubble(unit)

    def recreate_bubble(self, unit, text):
        self.remove_existing_bubble(unit)
        chat_bubble = ChatBubble(text, unit)
        self.chat_bubbles_by_names[unit.name] = chat_bubble
        task = Task(self.delete_bubble_after_no_updates, "delete bubble after no updates")
        core.instance.task_mgr.add(task, extraArgs=[task, unit.name])

    def remove_existing_bubble(self, unit):
        chat_bubble = self.chat_bubbles_by_names.get(unit.name, None)
        if chat_bubble is not None:
            chat_bubble.destroy()
            del self.chat_bubbles_by_names[unit.name]

    def delete_bubble_after_no_updates(self, task, name):
        """
        If the current bubble for unit exists long enough, we should destroy it.
        """
        current_time = datetime.now()
        bubble = self.chat_bubbles_by_names.get(name, None)
        if bubble is not None:
            if current_time - bubble.creation_time > timedelta(milliseconds=self.seconds_per_bubble * 1000):
                bubble.destroy()
                del self.chat_bubbles_by_names[name]
                return Task.done
            else:
                return Task.cont
        return Task.done


class ChatBubble:
    def __init__(self, text, unit):
        self.creation_time = datetime.now()
        font = MainFont()
        frame_padding = 0.3
        half_frame_length = len(text) * 0.1 + frame_padding
        self.bubble_text = DirectLabel(
            text=text,
            pos=(0, 0, 0.66),
            scale=0.04,
            parent=unit.base_node,
            text_bg=(0, 0, 0, 0),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            text_font=font,
        )
        self.bubble_frame = DirectFrame(
            pos=(0, 0.01, 0.67),
            scale=0.1,
            parent=unit.base_node,
            frameColor=(0, 0, 0, 0.5),
            frameSize=(-half_frame_length, half_frame_length, -0.5, 0.5)
        )

        self.bubble_text.set_compass(core.instance.camera)
        self.bubble_frame.set_compass(core.instance.camera)

    def destroy(self):
        self.bubble_text.destroy()
        self.bubble_frame.destroy()

