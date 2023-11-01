from .base import UInt8, String, BaseModel


class NameUpdate(BaseModel):
    id = UInt8
    name = String
