from .base import TaskPerformerBase
from ...storage.domain.disconnection import Disconnection
from datetime import datetime, timedelta
from protocol.messages.ConnectionCheckResponse import ConnectionCheckResponse
from direct.distributed.PyDatagram import PyDatagram
import json
import dataclasses
from ...event import event
from server.event.event import Event
from server.event.event_user import EventUser
import logging
from server import config

log = logging.getLogger(__name__)


class ConnectionChecker(TaskPerformerBase, EventUser):
    INTERVAL: int = config.connection_check_interval

    def __init__(self, session, connection, server):
        TaskPerformerBase.__init__(self, session, connection, server)
        EventUser.__init__(self, host=config.redis_host)
        self.last_connection_check = datetime.now()
        self.session.player_cache.subscribe_connection_check(self)

    def __call__(self, message):
        self.last_connection_check = datetime.now()

    def task_tick(self):
        tick_time = datetime.now()
        time_diff = tick_time - self.last_connection_check
        if time_diff < timedelta(milliseconds=config.connection_check_timeout * 1000):
            datagram = PyDatagram()
            message = ConnectionCheckResponse.build()
            message.dump(datagram)
            self.server.writer.send(datagram, self.connection)
        else:
            log.info(f"Timeout on player {self.session.player.name}")
            self.session.player_cache.delete()
            self.session.player_cache.publish_disconnect()
            self.send_event(event=Event.CLIENT_DISCONNECTION_PUBLISHED, prepared_data=self.connection)
            self._continue = False





