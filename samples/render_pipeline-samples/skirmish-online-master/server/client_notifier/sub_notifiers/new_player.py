from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event

import logging

log = logging.getLogger(__name__)


class NewPlayerNotifier(SubNotifierBase):
    MESSAGE = messages.NewPlayerResponse
    EVENT = Event.NEW_PLAYER_JOINED
    DROP_FOR_SELF = True

    def update_cache(self, data):
        self.event_notifier.session.player_position_cache.update_position(data)
