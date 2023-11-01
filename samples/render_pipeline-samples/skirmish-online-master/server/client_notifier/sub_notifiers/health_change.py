from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import logging

log = logging.getLogger(__name__)


class HealthUpdateNotifier(SubNotifierBase):
    MESSAGE = messages.HealthUpdateResponse
    EVENT = Event.HEALTH_UPDATED
