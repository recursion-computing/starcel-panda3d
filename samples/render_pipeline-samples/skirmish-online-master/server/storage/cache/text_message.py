from ..domain import TextMessage
import logging
from server.event.event_user import EventUser
from server.event.event import Event
from datetime import datetime


log = logging.getLogger(__name__)


class TextMessageCache(EventUser):

    def __init__(self, session):
        super().__init__()
        self.session = session
        self.accept_event(Event.PLAYER_DIED, handler=self.handle_player_died)

    def publish_text_message(self, text_message: TextMessage):
        """
        Broadcasts a spell.
        """
        self.send_event(
            event=Event.TEXT_MESSAGE,
            prepared_data=text_message,
        )

    def handle_player_died(self, args):
        player_id = args[0]
        killer_name = args[1]
        if self.session.player.id == player_id:
            text_message = TextMessage(
                player_name=self.session.player.name,
                send_dtime=datetime.now(),
                message=f"Killed by {killer_name}.",
            )
            self.publish_text_message(text_message)

    def send_kill_count_increased(self, kill_count):
        text_message = TextMessage(
            player_name=self.session.player.name,
            send_dtime=datetime.now(),
            message=f"Kill count: {kill_count}.",
        )
        self.publish_text_message(text_message)

    def send_playing_sound(self, file):
        text_message = TextMessage(
            player_name=self.session.player.name,
            send_dtime=datetime.now(),
            message=f"<<<playing {file}>>",
        )
        self.publish_text_message(text_message)


