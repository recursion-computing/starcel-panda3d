from .request_handler import Handler
from .storage.session import SessionManager
from .client_notifier.notifier import NotifierManager
from .tasking import TaskManager
from .event.event_user import EventUser
from .event.event import Event

from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from panda3d.core import PointerToConnection
from panda3d.core import NetAddress
from panda3d.core import NetDatagram

from threading import Thread
import time
import json
import logging


log = logging.getLogger(__name__)


class Server(EventUser):
    def __init__(self):
        super().__init__()

        # Support objects
        self.manager = QueuedConnectionManager()
        self.listener = QueuedConnectionListener(self.manager, 0)
        self.reader = QueuedConnectionReader(self.manager, 0)
        self.writer = ConnectionWriter(self.manager, 0)
        self.handler = Handler(self)

        # Server model
        self.session_manager = SessionManager()
        self.notifier_manager = NotifierManager(self)
        self.task_manager = TaskManager(self)
        self.connections = []

        # Socket
        self.tcp_socket = self.manager.open_TCP_server_rendezvous(15000, 1000)
        self.listener.add_connection(self.tcp_socket)

        self.accept_event(Event.CLIENT_DISCONNECTION_PUBLISHED, self.close_connection)

    def run(self):
        """
        Creates threads with active targets for accepting new connections and
        receiving data from existing ones
        """
        Thread(target=self.listen_for_new_connections, daemon=True).start()
        Thread(target=self.listen_for_new_data, daemon=True).start()

    def listen_for_new_connections(self):
        """
        Listens to new connections, when avalibe, creates new session
        and event notifier
        """
        while True:
            if self.listener.new_connection_available():
                rendezvous = PointerToConnection()
                net_address = NetAddress()
                new_connection = PointerToConnection()
                if self.listener.get_new_connection(
                    rendezvous, net_address, new_connection
                ):
                    new_connection = new_connection.p()

                    session = self.session_manager.new_session(
                        new_connection,
                    )

                    self.connections.append(new_connection)
                    self.notifier_manager.new_notifier(session, new_connection)
                    self.task_manager.new_session_task_manager(session, new_connection)
                    self.reader.add_connection(new_connection)

    def listen_for_new_data(self):
        """
        Listens for new data from active connections
        """
        while True:
            if self.reader.data_available():
                datagram = NetDatagram()
                if self.reader.get_data(datagram):
                    connection = datagram.getConnection()
                    session = self.session_manager.for_connection(connection)
                    self.handler.handle_data(
                        datagram,
                        connection,
                        session,
                    )
            time.sleep(0.01)

    def close_connection(self, connection):
        self.manager.close_connection(connection)
        self.connections.remove(connection)

    def find_connection_by_hash(self, connection_hash):
        for connection in self.connections:
            if hash(connection) == connection_hash:
                return connection



