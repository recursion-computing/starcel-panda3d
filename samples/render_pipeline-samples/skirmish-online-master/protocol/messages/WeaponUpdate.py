from .base import Message, MessageType, UInt8
from ..domain import WeaponUpdate


class WeaponUpdateMessage(Message):
    ID = UInt8(5)
    SCHEMA = WeaponUpdate
    TYPE = MessageType.response

