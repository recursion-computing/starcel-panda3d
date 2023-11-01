from .Player import Player
from .base import ListOf, BaseModel


class WorldState(BaseModel):
    player = Player
    other_players = ListOf(Player).customize(required=False)
