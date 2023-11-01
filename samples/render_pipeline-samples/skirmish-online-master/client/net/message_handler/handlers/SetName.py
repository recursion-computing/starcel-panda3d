from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages

import logging


log = logging.getLogger(__name__)


class SetNameHandler(MessageHandler):
    handled_message = messages.SetNameResponse
    response_message = None

    def handle_message(self):
        data = self.message.data
        core.instance.messenger.send(
            Event.UNIT_NAME_RECEIVED,
            sentArgs=[data.id, data.name],
        )
