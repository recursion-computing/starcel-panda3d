from .base import Message, MessageType, UInt8
from ..domain import CombatData


class CombatDataResponse(Message):
    ID = UInt8(55)
    SCHEMA = CombatData
    TYPE = MessageType.response
