from typing import List, Optional, Union
from enum import Enum
import dataclasses
from ..domain.base import ObjectBase, UInt8, String
import logging


log = logging.getLogger(__name__)


class MessagesBank:
    class RequestMessagesBank:
        messages = []
        messages_by_id = {}

    class ResponseMessagesBank:
        messages = []
        messages_by_id = {}

    @classmethod
    def register(cls, message_cls: "Message") -> None:
        if message_cls.TYPE is None:
            return

        bank = cls.bank_for_type(message_cls.TYPE)

        if message_cls.ID in bank.messages_by_id:
            raise Exception(
                f"message_cls {bank.messages_by_id[message_cls.ID]} and {message_cls} share the same ID!"
            )

        bank.messages.append(message_cls)
        bank.messages_by_id[message_cls.ID] = message_cls

    @classmethod
    def bank_for_type(cls, type_: "MessageType") -> type:
        return {
            MessageType.request: cls.RequestMessagesBank,
            MessageType.response: cls.ResponseMessagesBank,
        }[type_]

    @classmethod
    def by_id(cls, _id: int, type_: "MessageType") -> "Message":
        bank = cls.bank_for_type(type_)
        return bank.messages_by_id[_id]


class MetaClass(type):
    def __new__(cls, clsname, bases, attrs):
        newclass = super(MetaClass, cls).__new__(cls, clsname, bases, attrs)
        MessagesBank.register(newclass)
        return newclass


class MessageType(Enum):
    request = "Request"
    response = "Response"


class Message(metaclass=MetaClass):
    ID: UInt8
    SCHEMA: Optional[ObjectBase] = None
    TYPE: MessageType = None

    def __init__(self, data: Optional[ObjectBase] = None):
        self.data = data

    @classmethod
    def build(cls, value=None, **kwargs) -> "Message":
        if cls.SCHEMA is None:
            return cls()

        model = cls.SCHEMA

        if value is None:
            data = model.build(**kwargs)
        elif isinstance(value, model):
            data = value
        elif isinstance(value, (tuple, list)):
            data = model.build(*value, **kwargs)
        elif isinstance(value, dict):
            data = model.build(**value, **kwargs)
        elif dataclasses.is_dataclass(value):
            data = model.from_dataclass(value)
        else:
            data = model.build(value)
            # will raise if incompatibile
        return cls(data)

    @classmethod
    def parse(cls, iterator) -> "Message":
        if cls.SCHEMA is None:
            return cls()

        data = cls.SCHEMA.parse(iterator)
        return cls(data)

    def dump(self, datagram) -> None:
        self.ID.dump(datagram)

        if self.data is None:
            return

        self.data.dump(datagram)
