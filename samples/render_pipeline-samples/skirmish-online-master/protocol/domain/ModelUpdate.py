from .base import UInt8, BaseModel
from .Model import Model


class ModelUpdate(BaseModel):
    id = UInt8
    model = UInt8
