from .senders.animation import AnimationSender
from .senders.spell import SpellSender
from .senders.text_message import TextMessageSender
from .senders.position import PositionSender


class MessageSendersManager:
    def __init__(self, manager):
        """
        This class initializes and stores senders.
        """
        self.manager = manager
        self.senders = [
            AnimationSender(manager),
            SpellSender(manager),
            TextMessageSender(manager),
            PositionSender(manager),
        ]
