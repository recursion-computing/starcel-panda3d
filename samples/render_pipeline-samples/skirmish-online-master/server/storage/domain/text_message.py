from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class TextMessage:
    player_name: Optional[str]
    send_dtime: Optional[datetime]
    message: str
