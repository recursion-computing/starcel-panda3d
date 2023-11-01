from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import logging

log = logging.getLogger(__name__)


class SoundNotifier(SubNotifierBase):
    MESSAGE = messages.SoundResponse
    EVENT = Event.SOUND_REQUEST

