from .base import BaseSender
from client.event import Event
from protocol.messages import TextMessageRequest


class TextMessageSender(BaseSender):
    """
    Sends text messages
    """

    MANAGED_EVENT = Event.COMMAND_TO_SERVER_ENTERED
    MESSAGE_CLS = TextMessageRequest

    def handle(self, message: str) -> None:
        """
        Sends the text message
        """
        self.send(TextMessageRequest.build(message))
