import logging


log = logging.getLogger(__name__)


class SpellHandlersBank:
    handlers = []
    handlers_by_id = {}

    @classmethod
    def register(cls, handler) -> None:
        if handler.SPELL is None:
            return

        spell = handler.SPELL.value
        if spell in cls.handlers_by_id:
            raise Exception(
                f"handler_cls {cls.handlers_by_id[spell]} and {handler} share the same spell id!"
            )

        cls.handlers.append(handler)
        cls.handlers_by_id[spell] = handler

    @classmethod
    def by_spell(cls, spell: int):
        return cls.handlers_by_id[spell]


class MetaClass(type):
    def __new__(cls, clsname, bases, attrs):
        newclass = super(MetaClass, cls).__new__(cls, clsname, bases, attrs)
        SpellHandlersBank.register(newclass)
        return newclass
