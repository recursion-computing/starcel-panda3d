from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages


class ManaHandler(MessageHandler):
    handled_message = messages.ManaUpdateResponse
    response_message = None

    def handle_message(self):
        mana_info = self.message.data.data
        core.instance.messenger.send(
            Event.UNIT_MANA_RECEIVED,
            sentArgs=[mana_info],
        )
