import logging


log = logging.getLogger(__name__)


class TextCommandHandlerBank:
    handlers_by_keyword = {}

    @classmethod
    def register(cls, handler) -> None:
        if handler.KEYWORD is None:
            return

        keyword = handler.KEYWORD
        if keyword in cls.handlers_by_keyword:
            raise Exception(
                f"handler_cls {cls.handlers_by_keyword[keyword]} and {handler} share the same spell id!"
            )

        cls.handlers_by_keyword[keyword] = handler

    @classmethod
    def by_keyword(cls, keyword: str):
        return cls.handlers_by_keyword.get(keyword)


class MetaClass(type):
    def __new__(cls, clsname, bases, attrs):
        newclass = super(MetaClass, cls).__new__(cls, clsname, bases, attrs)
        TextCommandHandlerBank.register(newclass)
        return newclass
