from .base import Message, MessageType, UInt8
from ..domain import Animation, IdAnimation


class AnimationRequest(Message):
    ID = UInt8(51)
    SCHEMA = Animation
    TYPE = MessageType.request


class AnimationResponse(Message):
    ID = UInt8(51)
    SCHEMA = IdAnimation
    TYPE = MessageType.response
