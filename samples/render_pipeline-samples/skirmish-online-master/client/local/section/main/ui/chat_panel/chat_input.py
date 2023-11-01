from client.local.section.main.ui.text_panels.text_input import TextInput
from client.local import core
from client.event import Event


class ChatInput(TextInput):
    def __init__(self, parent_node):
        super().__init__(parent_node)

    def handle_input(self, text_input):
        core.instance.messenger.send(
            event=Event.COMMAND_TO_SERVER_ENTERED, sentArgs=[text_input]
        )
