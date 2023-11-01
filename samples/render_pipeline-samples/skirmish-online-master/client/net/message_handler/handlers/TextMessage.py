from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages

import logging


log = logging.getLogger(__name__)


class TextMessageHandler(MessageHandler):
    handled_message = messages.TextMessageResponse
    response_message = None

    def handle_message(self):
        data = self.message.data
        name, time, msg = data.player_name, data.send_dtime, data.message
        if time is not None:
            time = time._json()
        core.instance.messenger.send(Event.MSG_RECEIVED, sentArgs=[name, time, msg])
