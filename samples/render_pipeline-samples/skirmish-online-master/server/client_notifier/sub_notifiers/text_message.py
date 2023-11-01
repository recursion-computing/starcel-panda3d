from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import logging

log = logging.getLogger(__name__)


class TextMessageNotifier(SubNotifierBase):
    MESSAGE = messages.TextMessageResponse
    EVENT = Event.TEXT_MESSAGE

