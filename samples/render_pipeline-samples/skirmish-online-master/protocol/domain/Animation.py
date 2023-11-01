from .base import BaseModel, UInt8, String, Enum


class AnimationName(Enum):
    Stand = "stand"
    Run = "run"
    MeleAttack1 = "melee_attack_1"
    MeleAttack2 = "melee_attack_2"
    MagicAttack1 = "magic_attack_1"


class Animation(BaseModel):
    animation_name = String.customize(accepted_values=AnimationName)
    loop = UInt8


class IdAnimation(BaseModel):
    id = UInt8
    animation_name = String.customize(accepted_values=AnimationName)
    loop = UInt8
