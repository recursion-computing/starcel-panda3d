from .base import Message, MessageType, UInt8
from ..domain import Spell


class SpellRequest(Message):
    ID = UInt8(52)
    SCHEMA = Spell
    TYPE = MessageType.request
