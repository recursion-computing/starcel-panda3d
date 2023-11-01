from .base import UInt8, BaseModel
from .Weapon import Weapon


class WeaponUpdate(BaseModel):
    id = UInt8
    weapon_id = UInt8
