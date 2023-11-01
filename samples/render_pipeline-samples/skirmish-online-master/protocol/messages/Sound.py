from .base import Message, MessageType, UInt8
from ..domain import Sound


class SoundResponse(Message):
    ID = UInt8(152)
    SCHEMA = Sound
    TYPE = MessageType.response
