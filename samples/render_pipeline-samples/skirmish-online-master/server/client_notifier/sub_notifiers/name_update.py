from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import logging

log = logging.getLogger(__name__)


class NameUpdateNotifier(SubNotifierBase):
    MESSAGE = messages.SetNameResponse
    EVENT = Event.NAME_UPDATED

