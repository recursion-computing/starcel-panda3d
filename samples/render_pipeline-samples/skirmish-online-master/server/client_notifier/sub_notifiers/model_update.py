from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import logging

log = logging.getLogger(__name__)


class ModelUpdateNotifier(SubNotifierBase):
    MESSAGE = messages.ModelUpdateMessage
    EVENT = Event.MODEL_UPDATED
