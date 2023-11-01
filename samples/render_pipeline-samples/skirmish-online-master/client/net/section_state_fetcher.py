from protocol.domain.WorldState import WorldState
from protocol.messages.WorldState import WorldStateRequest
from protocol.parser import MessageParser, MessageType

from panda3d.core import NetDatagram
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator


class SectionStateFetcher:
    """
    Responsible for fetching the model of a section.
    """

    def __init__(self, net_client):
        self.net_client = net_client
        self.message_parser = MessageParser()

    def get_main_section_state(self) -> WorldState:
        """
        Fetch current world model from the server.
        """
        # send datagram asking for current world data (player's location, other player names, positions etc.)
        data = PyDatagram()
        data.add_uint8(WorldStateRequest.ID)
        self.net_client.writer.send(data, self.net_client.server_connection)

        # wait for datagram from the server
        self.net_client.manager.wait_for_readers(self.net_client.timeout / 1000)

        if not self.net_client.reader.data_available():
            raise Exception("No response from the server about the main section model.")

        datagram = NetDatagram()

        if not self.net_client.reader.get_data(datagram):
            raise Exception("Main section model response unavailable.")

        iterator = PyDatagramIterator(datagram)
        world_state_message = self.message_parser(iterator, MessageType.response)
        return world_state_message.data
