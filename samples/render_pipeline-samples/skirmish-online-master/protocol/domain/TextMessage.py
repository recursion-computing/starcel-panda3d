from .base import BaseModel, String, DateTime


class TextMessage(BaseModel):
    message = String
    player_name = String.customize(required=False)
    send_dtime = DateTime.customize(required=False)
