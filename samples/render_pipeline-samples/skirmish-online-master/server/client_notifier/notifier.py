from .sub_notifiers.positon_update import PositionUpdateNotifier
from .sub_notifiers.new_player import NewPlayerNotifier
from .sub_notifiers.animation_update import AnimationUpdateNotifier
from .sub_notifiers.health_change import HealthUpdateNotifier
from .sub_notifiers.mana_change import ManaUpdateNotifier
from .sub_notifiers.text_message import TextMessageNotifier
from .sub_notifiers.name_update import NameUpdateNotifier
from .sub_notifiers.model_update import ModelUpdateNotifier
from .sub_notifiers.weapon_update import WeaponUpdateNotifier
from .sub_notifiers.disconnect import DisconnectionNotifier
from .sub_notifiers.combat_data import CombatDataNotifier
from .sub_notifiers.scale_update import ScaleUpdateNotifier
from .sub_notifiers.not_enough_mana import NotEnoughManaNotifier
from .sub_notifiers.sound import SoundNotifier
from server.event.event_user import EventUser
from server.event.event import Event
from server import config

from redis import Redis
from direct.distributed.PyDatagram import PyDatagram
import logging


log = logging.getLogger(__name__)


class NotifierManager(EventUser):
    def __init__(self, server):
        """
        Accommodates all notifiers (for every connection there's one notifier)
        """
        super().__init__()
        self.server = server
        self.notifiers = {}
        self.accept_event(
            event=Event.CLIENT_DISCONNECTION_PUBLISHED,
            handler=self.handle_client_disconnection_published
        )

    def new_notifier(self, session, connection):
        """
        Produce new notifier for connection
        """
        self.notifiers[connection] = ClientNotifier(self.server, session, connection)

    def handle_client_disconnection_published(self, connection):
        del self.notifiers[connection]


class ClientNotifier:

    def __init__(self, server, session, connection):
        """
        EventNotifier notifies user of the session about some events/changes in the game state, e.g other player's
        animation being changed.

        For every event there's a separate sub-notifier.
        """
        super().__init__()
        self.server = server
        self.session = session
        self.connection = connection

        self.redis = Redis(host=config.redis_host)

        self.sub_notifiers = [
            PositionUpdateNotifier(self),
            NewPlayerNotifier(self),
            AnimationUpdateNotifier(self),
            HealthUpdateNotifier(self),
            ManaUpdateNotifier(self),
            TextMessageNotifier(self),
            NameUpdateNotifier(self),
            ModelUpdateNotifier(self),
            WeaponUpdateNotifier(self),
            DisconnectionNotifier(self),
            CombatDataNotifier(self),
            ScaleUpdateNotifier(self),
            NotEnoughManaNotifier(self),
            SoundNotifier(self)
        ]
        for sub_notifier in self.sub_notifiers:
            sub_notifier.start_listening()

    def notify(self, message):
        """
        Method called by sub notifiers to send a message
        """
        if self.session.ready_for_continuous_sync:
            datagram = PyDatagram()
            message.dump(datagram)
            self.server.writer.send(datagram, self.connection)