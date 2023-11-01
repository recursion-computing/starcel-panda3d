from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import logging

log = logging.getLogger(__name__)


class AnimationUpdateNotifier(SubNotifierBase):
    MESSAGE = messages.AnimationResponse
    EVENT = Event.ANIMATION_UPDATED
