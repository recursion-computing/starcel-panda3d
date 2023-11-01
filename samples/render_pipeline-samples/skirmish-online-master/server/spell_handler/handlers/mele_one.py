from .base import BaseSpellHandler
from typing import List
from protocol.domain import Spells, AnimationName
import random


class MeleOneHandler(BaseSpellHandler):
    SPELL = Spells.mele_one
    ANIMATION = AnimationName.MeleAttack1
    DAMAGE_RANGE = (15, 20)
    MANA_COST = 8
    AOE_RANGE = 0.4

