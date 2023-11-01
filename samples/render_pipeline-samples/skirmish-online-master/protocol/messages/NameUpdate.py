from .base import Message, MessageType, UInt8
from ..domain import NameUpdate


class SetNameResponse(Message):
    ID = UInt8(4)
    SCHEMA = NameUpdate
    TYPE = MessageType.response
