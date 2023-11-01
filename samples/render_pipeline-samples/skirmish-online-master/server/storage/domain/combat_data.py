from dataclasses import dataclass
from typing import List


@dataclass
class CombatData:
    spell: int
    hp_change: int
    source: int
    targets: List[int]
