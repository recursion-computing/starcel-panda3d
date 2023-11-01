from .base import BaseTextCommandHandler

import logging

log = logging.getLogger(__name__)


class SetNameCommandHandler(BaseTextCommandHandler):
    KEYWORD = "/setname"
    LENGTH = 1

    def handle_command(self):
        new_name = self.command_vector[1]
        log.info(f"{self.session.player.name} changed their name to '{new_name}'.")
        self.session.player_cache.publish_name_update(new_name)



