from .base import Message, UInt8, MessageType
from ..domain.base import ListOf
from ..domain import HealthUpdate


class HealthUpdateResponse(Message):
    ID = UInt8(103)
    SCHEMA = ListOf(HealthUpdate)
    TYPE = MessageType.response
