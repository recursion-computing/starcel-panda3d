from abc import abstractmethod
from protocol.messages.base import Message
from typing import Optional, Any
from .bank import MetaClass


class MessageHandler(metaclass=MetaClass):
    handled_message: Message = None

    def __init__(self, message: Message):
        self.message = message

    def __call__(self) -> Optional[Any]:
        """
        Method called by root handler distributing
        messages.
        """
        self.handle_message()

    @abstractmethod
    def handle_message(self):
        """
        Method for handling self.message
        """
        pass
