from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import logging

log = logging.getLogger(__name__)


class CombatDataNotifier(SubNotifierBase):
    MESSAGE = messages.CombatDataResponse
    EVENT = Event.COMBAT_DATA_CREATED
