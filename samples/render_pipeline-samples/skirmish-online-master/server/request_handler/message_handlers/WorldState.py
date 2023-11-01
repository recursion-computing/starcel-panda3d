from .base import MessageHandler
from protocol import messages
import logging


log = logging.getLogger(__name__)


class WorldStateHandler(MessageHandler):
    handled_message = messages.WorldStateRequest
    response_message = messages.WorldStateResponse

    def __call__(self) -> messages.WorldStateResponse:
        """
        Build session and return world model
        """
        current_players = self.session.player_cache.all_players()
        id_ = max({p.id for p in current_players} | {-1}) + 1

        self.session.for_player(id_)
        self.session.spell_cache.initialize_trigger_times()
        log.info(f"{self.session.player.name} joined the game.")
        message = messages.WorldStateResponse.build(
            player=self.session.player,
            other_players=current_players,
        )
        return message
