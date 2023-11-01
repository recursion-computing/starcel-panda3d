from protocol.messages import MessageType
from protocol.messages.base import Message
from .handlers import MessageHandlersBank
from protocol.parser import MessageParser

from panda3d.core import QueuedConnectionManager
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

import logging


log = logging.getLogger(__name__)


class Handler:
    def __init__(self, net_client):
        """
        Base handler for new data.

        The idea of handler is to delegate new requests to subhandlers.
        Each subhandler has to implement procedure of handling upcoming
        data and then providing response, if any.

        In order to handle new massages write additional handlers in message
        handlers submodule.
        """
        self.net_client = net_client
        self.message_parser = MessageParser()

    def handle_data(self, datagram: PyDatagram) -> None:
        """
        Handling new data.

        First, message is obtained, then correct message handler is called
        """
        iterator = PyDatagramIterator(datagram)
        # parse message
        try:
            message = self.message_parser(iterator, MessageType.response)
            response = self.handle_message(message)
            self.handle_response(response)

        except KeyError as e:
            log.exception(e)
            log.error("Unsupported message.")
            return

    def handle_message(self, message: Message) -> None:
        """
        Call correct message handler
        """
        try:
            handler = MessageHandlersBank.by_id(message.ID)(message)
        except KeyError as e:
            log.exception(e)
            log.error("Unsupported operation.")
            return
        return handler()

    def handle_response(self, response) -> None:
        """
        Send response to message, if any
        """
        if response is None:
            return

        response_datagram = PyDatagram()
        response.dump(response_datagram)
        self.net_client.writer.send(response_datagram, self.net_client.server_connection)