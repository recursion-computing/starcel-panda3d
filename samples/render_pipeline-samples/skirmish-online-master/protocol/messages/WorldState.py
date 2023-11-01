from .base import Message, MessageType, UInt8
from ..domain import WorldState


class WorldStateRequest(Message):
    ID = UInt8(1)
    TYPE = MessageType.request


class WorldStateResponse(Message):
    ID = UInt8(1)
    SCHEMA = WorldState
    TYPE = MessageType.response
