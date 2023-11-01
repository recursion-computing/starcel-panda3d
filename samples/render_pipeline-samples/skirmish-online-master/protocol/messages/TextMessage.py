from .base import Message, MessageType, UInt8, String
from ..domain import TextMessage


class TextMessageRequest(Message):
    ID = UInt8(54)
    SCHEMA = String
    TYPE = MessageType.request


class TextMessageResponse(Message):
    ID = UInt8(54)
    SCHEMA = TextMessage
    TYPE = MessageType.response
