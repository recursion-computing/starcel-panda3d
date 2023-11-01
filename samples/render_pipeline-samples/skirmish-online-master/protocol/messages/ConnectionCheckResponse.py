from .base import Message, MessageType, UInt8


class ConnectionCheckResponse(Message):
    ID = UInt8(159)
    TYPE = MessageType.response


class ConnectionCheckRequest(Message):
    ID = UInt8(159)
    TYPE = MessageType.request

