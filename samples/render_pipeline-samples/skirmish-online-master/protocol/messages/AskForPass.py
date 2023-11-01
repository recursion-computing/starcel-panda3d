from .base import Message, UInt8


class AskForPass(Message):
    ID = UInt8(0)
