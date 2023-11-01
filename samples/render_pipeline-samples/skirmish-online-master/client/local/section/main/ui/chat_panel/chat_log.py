from client.local.section.main.ui.text_panels.text_log import TextLog
from client.event import Event


class ChatLog(TextLog):
    def __init__(self, parent_node):
        super().__init__(parent_node, width=0.25, height=0.265, n_lines=12)
        self.accept(Event.MSG_RECEIVED, self.add_msg)
        self.accept(Event.NEW_UNIT_CREATED, self.handle_new_unit_created)
        self.accept(Event.UNIT_DELETED, self.handle_unit_deleted)
        self.accept(Event.UNIT_NAME_UPDATED, self.handle_unit_name_updated)

    def handle_new_unit_created(self, *args):
        unit = args[0]
        self.add_msg(name=None, time=None, msg=f"{unit.name} has joined the game.")

    def handle_unit_deleted(self, *args):
        unit_name = args[0]
        self.add_msg(name=None, time=None, msg=f"{unit_name} has left the game.")

    def handle_unit_name_updated(self, *args):
        unit = args[0]
        old_name = args[1]
        self.add_msg(name=None, time=None, msg=f"{old_name} changed their name to '{unit.name}'.")

    def add_msg(self, name, time, msg):
        if name is None:
            lines = msg.splitlines()
        else:
            lines = [f"[{time}] {name}: {msg}"]
        for line in lines:
            self.add_line(line)
        self.update_view()
