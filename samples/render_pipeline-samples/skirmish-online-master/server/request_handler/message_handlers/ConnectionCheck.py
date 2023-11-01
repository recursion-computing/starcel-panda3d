from .base import MessageHandler
from protocol import messages, domain
import logging


log = logging.getLogger(__name__)


class ConnectionCheckHandler(MessageHandler):
    handled_message = messages.ConnectionCheckRequest
    response_message = None

    def handle_message(self):
        self.session.player_cache.send_connection_check_event()
