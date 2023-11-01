from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages

import logging


log = logging.getLogger(__name__)


class SetModelHandler(MessageHandler):
    handled_message = messages.ModelUpdateMessage
    response_message = None

    def handle_message(self):
        data = self.message.data
        core.instance.messenger.send(
            Event.UNIT_MODEL_RECEIVED,
            sentArgs=[data.id, data.model],
        )
