from .base import BaseModel, ListOf, UInt8
from .Spell import Spells


class CombatData(BaseModel):
    spell = UInt8.customize(accepted_values=Spells)
    hp_change = UInt8
    source = UInt8
    targets = ListOf(UInt8)
