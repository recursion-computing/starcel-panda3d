from .messages import MessagesBank
from .messages.base import Message, MessageType


class MessageParser:
    def message_by_id(self, _id: int, type_: MessageType) -> Message:
        return MessagesBank.by_id(_id, type_)

    def __call__(self, iterator, type_: MessageType):
        return self.message_by_id(iterator.get_uint8(), type_).parse(iterator)
