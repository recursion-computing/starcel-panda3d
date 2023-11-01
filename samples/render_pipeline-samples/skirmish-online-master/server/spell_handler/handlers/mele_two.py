from .base import BaseSpellHandler
from typing import List
from protocol.domain import Spells, AnimationName


class MeleTwoHandler(BaseSpellHandler):
    SPELL = Spells.mele_two
    ANIMATION = AnimationName.MagicAttack1
    DAMAGE_RANGE = (26, 31)
    MANA_COST = 15
    AOE_RANGE = 0.4
