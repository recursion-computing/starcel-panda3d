from direct.actor.Actor import Actor
from protocol.domain import Player
from client.local.model.actor.base import ConfiguredActor
from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class Unit:
    x: float
    y: float
    z: float
    h: float
    p: float
    r: float
    id: int = -1
    name: str = "Unknown"
    health: int = 0
    mana: int = 50
    scale: float = 1
    actor: Optional[ConfiguredActor] = None
    model_id: Optional[int] = None
    animation_str: Optional[str] = None
    weapon_id: Optional[str] = None
    base_node: Optional[Any] = None
    weapon_node: Optional[Any] = None
    interpolator: Optional[Any] = None
    anim_mgr: Optional[Any] = None

    @classmethod
    def from_player(cls, player):
        """
        Special use case is initializing
        unit from Player
        """
        data = {
            "id": player.id,
            "name": player.name,
            "health": player.health,
            "model_id": player.model_id,
            "animation_str": player.animation,
            "weapon_id": player.weapon_id,
            "x": player.x,
            "y": player.y,
            "z": player.z,
            "h": player.h,
            "p": player.p,
            "r": player.r,
            "scale": player.scale
        }
        return cls(**data)
