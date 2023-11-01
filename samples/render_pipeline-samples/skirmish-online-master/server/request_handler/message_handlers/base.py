from abc import abstractmethod
from protocol.messages.base import Message
from typing import Optional, Any
from .bank import MetaClass


class MessageHandler(metaclass=MetaClass):
    handled_message: Message = None
    response_message: Optional[Message] = None

    def __init__(self, session, message: Message):
        self.session = session
        self.message = message

    def __call__(self) -> Optional[Any]:
        """
        Method called by root handler distributing
        messages. By default, handler will first
        handle new message, then build response seperately.

        This design unsures, that basic requests only returning
        data or only handling it are easier to write.

        When handling complex procedures, where response is build
        from handled data context it is best just to overwrite this
        function
        """
        self.handle_message()
        return self.build_response()

    @abstractmethod
    def handle_message(self):
        """
        Method for handling self.message
        """
        pass

    def build_response(self) -> Optional[Message]:
        """
        Response builder
        """
        return None
