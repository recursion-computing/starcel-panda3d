from .base import MessageHandler
from ...storage.domain import TextMessage
from ...text_command_handler.handler import TextCommandHandler
from protocol import messages
from datetime import datetime
import logging

log = logging.getLogger(__name__)


class TextMessageHandler(MessageHandler):
    handled_message = messages.TextMessageRequest
    response_message = None

    def handle_message(self):
        """
        Check if the text message is a command, if yes then pass it to the command handler,
        otherwise distribute it to all players as a text message.
        """
        text_message_string = self.message.data

        word_vector = text_message_string.split()

        if TextCommandHandler.is_a_command(word_vector):
            TextCommandHandler(self.session, word_vector)()
            return

        text_message = TextMessage(
            player_name=self.session.player.name,
            send_dtime=datetime.now(),
            message=text_message_string,
        )

        log.info(f"{self.session.player.name} wrote: {text_message_string}")

        self.session.text_message_cache.publish_text_message(text_message)



