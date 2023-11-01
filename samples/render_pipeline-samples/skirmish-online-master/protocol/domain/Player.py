from .base import BaseModel, UInt8, String, Float64
from .Animation import AnimationName
from .Model import Model
from .Weapon import Weapon


class Player(BaseModel):
    id = UInt8
    name = String
    health = UInt8
    model_id = UInt8.customize(accepted_values=Model)
    animation = String.customize(accepted_values=AnimationName)
    weapon_id = UInt8.customize(accepted_values=Weapon)

    x = Float64
    y = Float64
    z = Float64
    h = Float64
    p = Float64
    r = Float64

    scale = Float64


class PlayerPosHPR(BaseModel):
    x = Float64
    y = Float64
    z = Float64
    h = Float64
    p = Float64
    r = Float64


class PlayerIdPosHPR(BaseModel):
    id = UInt8
    x = Float64
    y = Float64
    z = Float64
    h = Float64
    p = Float64
    r = Float64
