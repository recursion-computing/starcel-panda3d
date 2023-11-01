from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages

import logging


log = logging.getLogger(__name__)


class PosRotHandler(MessageHandler):
    handled_message = messages.PosHPRResponse
    response_message = None

    def handle_message(self):
        data = self.message.data
        core.instance.messenger.send(
            Event.UNIT_POS_ROT_RECEIVED,
            sentArgs=[data.id, data.x, data.y, data.z, data.h, data.p, data.r],
        )
