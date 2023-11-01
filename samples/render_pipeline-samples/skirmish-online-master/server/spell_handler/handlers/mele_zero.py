from .base import BaseSpellHandler
from typing import List
from protocol.domain import Spells, AnimationName


class MeleZeroHandler(BaseSpellHandler):
    SPELL = Spells.mele_zero
    ANIMATION = AnimationName.MeleAttack1
    DAMAGE_RANGE = (8, 15)
    MANA_COST = 5
    AOE_RANGE = 0.4
