from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import logging

log = logging.getLogger(__name__)


class ScaleUpdateNotifier(SubNotifierBase):
    MESSAGE = messages.ScaleUpdateResponse
    EVENT = Event.SCALE_UPDATED
