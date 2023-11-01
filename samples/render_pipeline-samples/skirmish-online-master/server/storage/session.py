from redis import Redis
import uuid
import logging
import json
from server.event.event_user import EventUser
from server.event.event import Event
from .cache.sessions import SessionCache
from .cache.players import PlayerCache
from .cache.player_position import PlayerPositionCache
from .cache.spells import SpellCache
from .cache.text_message import TextMessageCache
from server import config


log = logging.getLogger(__name__)


class SessionManager(EventUser):
    def __init__(self):
        """
        SessionManager is a container for all active sessions
        """
        super().__init__()
        self.sessions = {}
        self.accept_event(
            event=Event.CLIENT_DISCONNECTION_PUBLISHED,
            handler=self.handle_client_disconnection_published
        )

    def for_connection(self, connection):
        """
        Fetches session assigned for connection
        """
        return self.sessions[connection]

    def new_session(self, connection):
        """
        Creastes new session
        """
        session = Session()
        self.sessions[connection] = session
        return session

    def handle_client_disconnection_published(self, connection):
        del self.sessions[connection]


class Session:
    def __init__(self):
        """
        Creates empty session
        """
        self.id = uuid.uuid4().hex
        self.player = None
        self.redis = Redis(host=config.redis_host)

        self.cache = SessionCache(self)
        self.cache.store()

        self.player_cache = PlayerCache(self)
        self.player_position_cache = PlayerPositionCache(self)
        self.spell_cache = SpellCache(self)
        self.text_message_cache = TextMessageCache(self)
        self.ready_for_continuous_sync = False
        self.closed = False

    def dump(self):
        """
        Dump session data to json
        """
        return json.dumps(
            {
                "player": self.player.id if self.player is not None else None,
            }
        )

    def for_player(self, id_):
        """
        Load player
        """
        self.player = self.player_cache.load_or_create(id_)

    def set_position(self, position, send_to_owner=False):
        """
        Sets player position
        """
        position_update = self.player_cache.publish_position_update(position, send_to_owner)
        if position_update is not None:
            self.player = self.player_cache.load(self.player.id)
            self.player.update_position(position_update)
            self.player_cache.save(self.player)

    def teleport(self, position):
        self.set_position(position, send_to_owner=True)

    def set_animation(self, animation):
        """
        Sets player animation
        """
        animation_update = self.player_cache.publish_animation_update(
            animation,
        )
        self.player = self.player_cache.load(self.player.id)
        self.player.update_animation(animation_update)
        self.player_cache.save(self.player)

