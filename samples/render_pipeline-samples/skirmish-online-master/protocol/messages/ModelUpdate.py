from .base import Message, MessageType, UInt8
from ..domain import ModelUpdate


class ModelUpdateMessage(Message):
    ID = UInt8(2)
    SCHEMA = ModelUpdate
    TYPE = MessageType.response

