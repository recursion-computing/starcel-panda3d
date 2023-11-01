import pandas
import logging
from server.event.event_user import EventUser
from server.event.event import Event
from protocol.messages.PosHPR import PosHPRRequest
from random import randint

log = logging.getLogger(__name__)


class PlayerPositionCache(EventUser):
    def __init__(self, session):
        """
        PlayerPositionCache is cache of user positions.

        It provides easy searching for nearby players
        in rectangular areas and then allows to narrow
        down the search
        """
        super().__init__()
        self.session = session
        self.all_positions = pandas.DataFrame(columns=["x", "y", "z"], dtype=float)
        self.update_all_positions()
        self.accept_event(event=Event.PLAYER_DIED, handler=self.handle_player_died)

    def handle_player_died(self, args):
        player_id = args[0]
        if self.session.player.id == player_id:
            self.teleport_randomly()

    def teleport_randomly(self):
        self.session.teleport(
            PosHPRRequest.build(
                x=0,
                y=0,
                z=1,
                h=120,
                p=0,
                r=0,
            ).data
        )

    def update_position(self, player_position):
        """
        Updates player position in cache
        """
        self.all_positions.at[player_position.id] = {
            "x": player_position.x,
            "y": player_position.y,
            "z": player_position.z,
        }

    def update_all_positions(self):
        all_players = self.session.player_cache.all_players()
        for player in all_players:
            self.update_position(player)

    def remove_positions(self, player_ids):
        try:
            self.all_positions.drop(player_ids, inplace=True)
        except KeyError:
            pass

    def get_nearby(self, player_position, x_range, y_range, z_range):
        """
        Searches in rectangular area for nearby players
        to given player_position
        """
        result = set(
            self.all_positions.index[
                (self.all_positions["x"] >= player_position.x - x_range)
                & (self.all_positions["x"] <= player_position.x + x_range)
                & (self.all_positions["y"] >= player_position.y - y_range)
                & (self.all_positions["y"] <= player_position.y + y_range)
                & (self.all_positions["z"] >= player_position.z - z_range)
                & (self.all_positions["z"] <= player_position.z + z_range)
            ].tolist()
        ) - {player_position.id}
        return list(result)
