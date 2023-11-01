from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event
from server.storage.domain.player import PlayerPositionUpdate

import logging

log = logging.getLogger(__name__)


class NotEnoughManaNotifier(SubNotifierBase):
    MESSAGE = messages.NotEnoughMana
    EVENT = Event.NOT_ENOUGH_MANA
    DROP_FOR_OTHERS = True

