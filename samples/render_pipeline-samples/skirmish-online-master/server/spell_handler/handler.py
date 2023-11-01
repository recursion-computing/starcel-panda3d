from protocol.domain import CombatData, Spells
from .handlers import SpellHandlersBank
import logging

log = logging.getLogger(__name__)


class SpellHandler:
    def __init__(self, spell_data, session):
        """
        Handling of upcoming spells is done here, in this class.

        Implement veryfication, spell distinguish etc here.
        """
        self.spell_data = spell_data
        self.session = session

    def __call__(self) -> CombatData:
        """
        Handle the spell.
        """
        handler = self.get_handler()
        handler()
        #return CombatData.from_dataclass(handler())

    def get_handler(self):
        """
        Gets appropriate handler for the spell
        """
        handler_cls = SpellHandlersBank.by_spell(self.spell_data.spell)
        return handler_cls(self.session, self.spell_data)
