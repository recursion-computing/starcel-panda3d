from .base import Message, MessageType, UInt8
from ..domain import ScaleUpdate


class ScaleUpdateResponse(Message):
    ID = UInt8(151)
    SCHEMA = ScaleUpdate
    TYPE = MessageType.response
