from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import logging

log = logging.getLogger(__name__)


class WeaponUpdateNotifier(SubNotifierBase):
    MESSAGE = messages.WeaponUpdateMessage
    EVENT = Event.WEAPON_UPDATED

