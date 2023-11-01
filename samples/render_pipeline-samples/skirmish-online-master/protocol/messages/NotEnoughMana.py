from .base import Message, UInt8, MessageType


class NotEnoughMana(Message):
    ID = UInt8(211)
    TYPE = MessageType.response
