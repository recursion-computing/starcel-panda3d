from protocol import messages
from .base import SubNotifierBase
from server.event.event import Event
from server.storage.domain.player import PlayerPositionUpdate

import logging

log = logging.getLogger(__name__)


class PositionUpdateNotifier(SubNotifierBase):
    MESSAGE = messages.PosHPRResponse
    EVENT = Event.POSITION_UPDATED

    def drop(self, data: PlayerPositionUpdate):
        # we don't want to send this message if it's not intended to be sent to the subject of position
        return not data.send_to_owner and self.message_is_about_this_player(data)

    def update_cache(self, data: PlayerPositionUpdate):
        self.event_notifier.session.player_position_cache.update_position(data)
