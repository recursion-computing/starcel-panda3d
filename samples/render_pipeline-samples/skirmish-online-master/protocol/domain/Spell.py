from .base import BaseModel, UInt8
from enum import Enum


class Spells(Enum):
    mele_zero = 0
    mele_one = 1
    mele_two = 2
    mele_three = 3


class Spell(BaseModel):
    spell = UInt8.customize(accepted_values=Spells)
