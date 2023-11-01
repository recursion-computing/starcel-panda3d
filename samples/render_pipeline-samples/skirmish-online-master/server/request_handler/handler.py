from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.distributed.PyDatagram import PyDatagram
from protocol.parser import MessageParser
from protocol.messages import MessageType
from .message_handlers import MessageHandlersBank
import logging


log = logging.getLogger(__name__)


class Handler:
    def __init__(self, server):
        """
        Base handler for new data.

        The idea of handler is to delegate new requests to subhandlers.
        Each subhandler has to implement procedure of handling upcoming
        data and then providing response, if any.

        In order to handle new massages write additional hanlders in message
        handlers sub module.
        """
        self.server = server
        self.message_parser = MessageParser()

    def handle_data(self, datagram, connection, session):
        """
        Handling new data.

        First, message is obtained, then correct message handler is called
        """
        iterator = PyDatagramIterator(datagram)
        # parse message
        try:
            message = self.message_parser(iterator, MessageType.request)
        except KeyError as e:
            log.exception(e)
            log.error("unsuppoerted message")
            return
        # produce response
        response = self.handle_message(session, message)
        # send response
        self.handle_response(connection, response)

    def handle_response(self, connection, response) -> None:
        """
        Send response to message, if any
        """
        if response is None:
            return

        response_datagram = PyDatagram()
        response.dump(response_datagram)
        self.server.writer.send(response_datagram, connection)

    def handle_message(self, session, message):
        """
        Call correct message handler
        """

        try:
            handler = MessageHandlersBank.by_id(message.ID)(
                session,
                message,
            )
        except KeyError as e:
            log.exception(e)
            log.error("unsuppoerted operation")
            return
        return handler()
