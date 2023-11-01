from .base import TaskPerformerBase
import logging

log = logging.getLogger(__name__)


class ManaRegenerator(TaskPerformerBase):
    INTERVAL: int = 1
    AMOUNT: int = 6

    def task_tick(self):
        if self.session.player is not None:
            player_id_list = [self.session.player.id]
            if not self.session.closed:
                self.session.player_cache.publish_mana_update(player_id_list, -self.AMOUNT)
