from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages

import logging


log = logging.getLogger(__name__)


class SoundHandler(MessageHandler):
    handled_message = messages.SoundResponse
    response_message = None

    def handle_message(self):
        file = self.message.data.file
        path = f"client/local/assets/sounds/{file}"
        try:
            sound = core.instance.loader.load_sfx(path)
            sound.play()
        except:
            pass
