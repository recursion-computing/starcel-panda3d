from .base import BaseTextCommandHandler
from protocol.domain import Model
import logging

log = logging.getLogger(__name__)


class SetModelCommandHandler(BaseTextCommandHandler):
    KEYWORD = "/setmodel"
    LENGTH = 1

    def handle_command(self):
        new_model = self.command_vector[1]
        if int(new_model) in Model._value2member_map_:
            self.session.player_cache.publish_model_update(new_model)



