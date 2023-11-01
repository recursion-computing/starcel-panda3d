from .base import UInt8, BaseModel


class HealthUpdate(BaseModel):
    id = UInt8
    health = UInt8
