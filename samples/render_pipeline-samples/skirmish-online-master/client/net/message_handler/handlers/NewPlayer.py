from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages
from client.local.section.main.model.unit import Unit


class NewPlayerHandler(MessageHandler):
    handled_message = messages.NewPlayerResponse
    response_message = None

    def handle_message(self):
        data = self.message.data
        unit = Unit.from_player(data)
        core.instance.messenger.send(
            Event.NEW_UNIT_DATA_RECEIVED,
            sentArgs=[unit],
        )
