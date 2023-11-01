from .base import BaseTextCommandHandler
from protocol.domain import Weapon


import logging

log = logging.getLogger(__name__)


class SetWeaponCommandHandler(BaseTextCommandHandler):
    KEYWORD = "/setweapon"
    LENGTH = 1

    def handle_command(self):
        weapon_id = self.command_vector[1]
        if int(weapon_id) in Weapon._value2member_map_:
            self.session.player_cache.publish_weapon_update(weapon_id)



