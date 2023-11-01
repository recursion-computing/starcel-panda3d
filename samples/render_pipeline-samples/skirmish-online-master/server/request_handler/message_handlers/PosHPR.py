from .base import MessageHandler
from protocol import messages, domain
import logging


log = logging.getLogger(__name__)


class PosHPRHandler(MessageHandler):
    handled_message = messages.PosHPRRequest
    response_message = None

    def handle_message(self):
        player_pos = self.message.data
        self.session.set_position(player_pos)
