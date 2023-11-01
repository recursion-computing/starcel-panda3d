from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import json
import logging

log = logging.getLogger(__name__)


class DisconnectionNotifier(SubNotifierBase):
    MESSAGE = messages.DisconnectResponse
    EVENT = Event.DISCONNECTION

    def update_cache(self, data):
        self.event_notifier.session.player_position_cache.remove_positions([data.id])

