from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import logging

log = logging.getLogger(__name__)


class ManaUpdateNotifier(SubNotifierBase):
    MESSAGE = messages.ManaUpdateResponse
    EVENT = Event.MANA_UPDATED
