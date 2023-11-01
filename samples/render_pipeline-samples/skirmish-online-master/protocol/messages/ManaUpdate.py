from .base import Message, UInt8, MessageType
from ..domain.base import ListOf
from ..domain import ManaUpdate


class ManaUpdateResponse(Message):
    ID = UInt8(104)
    SCHEMA = ListOf(ManaUpdate)
    TYPE = MessageType.response
