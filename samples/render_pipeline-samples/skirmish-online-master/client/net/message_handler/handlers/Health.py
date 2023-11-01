from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages


class HealthHandler(MessageHandler):
    handled_message = messages.HealthUpdateResponse
    response_message = None

    def handle_message(self):
        health_info = self.message.data.data
        core.instance.messenger.send(
            Event.UNIT_HEALTH_RECEIVED,
            sentArgs=[health_info],
        )
