from .base import Message, MessageType, UInt8
from ..domain import PlayerPosHPR, PlayerIdPosHPR


class PosHPRRequest(Message):
    ID = UInt8(50)
    SCHEMA = PlayerPosHPR
    TYPE = MessageType.request


class PosHPRResponse(Message):
    ID = UInt8(50)
    SCHEMA = PlayerIdPosHPR
    TYPE = MessageType.response
