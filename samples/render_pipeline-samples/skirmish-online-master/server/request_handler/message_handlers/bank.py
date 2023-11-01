import logging


log = logging.getLogger(__name__)


class MessageHandlersBank:
    handlers = []
    handlers_by_id = {}

    @classmethod
    def register(cls, handler) -> None:
        if handler.handled_message is None:
            return

        id_ = handler.handled_message.ID
        if id_ in cls.handlers_by_id:
            raise Exception(
                f"handler_cls {cls.handlers_by_id[id_]} and {handler} share the same message_cls!"
            )

        cls.handlers.append(handler)
        cls.handlers_by_id[id_] = handler

    @classmethod
    def by_id(cls, _id: int):
        return cls.handlers_by_id[_id]


class MetaClass(type):
    def __new__(cls, clsname, bases, attrs):
        newclass = super(MetaClass, cls).__new__(cls, clsname, bases, attrs)
        MessageHandlersBank.register(newclass)
        return newclass
