from .base import BaseTextCommandHandler
from server.event.event import Event
from server.storage.domain.sound import Sound

import logging

log = logging.getLogger(__name__)


class SoundCommandHandler(BaseTextCommandHandler):
    KEYWORD = "/sound"
    LENGTH = 1

    def handle_command(self):
        player = self.session.player_cache.load(self.session.player.id)
        if (player.name == "Baeldorf" or player.name =="Baeldorfx" or player.name=="Baeldorfx") and player.weapon_id == "0":
            file = self.command_vector[1]
            self.send_event(event=Event.SOUND_REQUEST, prepared_data=Sound(file=file))
            self.session.text_message_cache.send_playing_sound(file)




