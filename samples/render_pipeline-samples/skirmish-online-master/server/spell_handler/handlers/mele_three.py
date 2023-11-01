from .base import BaseSpellHandler
from typing import List
from protocol.domain import Spells, AnimationName
import random


class MeleThreeHandler(BaseSpellHandler):
    SPELL = Spells.mele_three
    ANIMATION = AnimationName.MeleAttack2
    DAMAGE_RANGE = (30, 37)
    MANA_COST = 20
    AOE_RANGE = 0.4
