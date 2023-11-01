from ..domain import Player, PlayerPositionUpdate, PlayerAnimationUpdate, HealthUpdate, NameUpdate, ModelUpdate, WeaponUpdate, Disconnection, ManaUpdate, ScaleUpdate, NotEnoughMana, Sound
from server.event.event_user import EventUser
from server.event.event import Event
import json
import dataclasses
import logging
from datetime import datetime, timedelta
from protocol.domain import Weapon, Model
import random
from server import config

log = logging.getLogger(__name__)


class PlayerCache(EventUser):
    SET_KEY = "players"
    PREFIX = "player_"

    def __init__(self, session):
        super().__init__()
        self.session = session
        self.last_position_update = datetime.now()
        self.CONNECTION_CHECK_EVENT = "connection_check_" + self.session.id
        self.accept_event(event=Event.PLAYER_DIED, handler=self.handle_player_died)

    def key(self, id_=None):
        """
        Prefixed key for session
        """
        if id_ is None:
            id_ = self.session.player.id
        if isinstance(id_, bytes):
            return f"{self.PREFIX}{id_.decode()}"
        return f"{self.PREFIX}{id_}"

    def load(self, id_):
        """
        Loads player
        """
        player_data = self.session.redis.get(self.key(id_))
        assert player_data is not None, self.key(id_)
        return Player(**json.loads(player_data))

    def load_or_create(self, id_):
        """
        Loads player or creates new
        """
        try:
            return self.load(id_)
        except AssertionError:
            return self.create_from_id(id_)

    def create_from_id(self, id_):
        """
        Creates new user from id_
        """

        model = random.choice([m.value for m in Model])
        name = {0: "Dark Elf", 1: "Elf", 2: "Kamael", 3: "Dwarf"}[model]
        name = f"{name} [{id_}]"

        player = Player(
            id=id_,
            health=50,
            mana=50,
            model_id=model,
            name=name,
            animation="stand",
            loop=1,
            weapon_id=random.choice([w.value for w in Weapon]),
            x=-3,
            y=-5,
            z=1,
            h=120,
            p=0,
            r=0,
            scale=1,
            power=1,
            kill_count=0,
        )
        self.publish_new_player(player)
        return player

    def save(self, player):
        """
        Saves player
        """
        self.session.redis.set(
            self.key(player.id), json.dumps(dataclasses.asdict(player))
        )

    def delete(self):
        """
        Delete player from redis cache.
        """
        self.session.redis.delete(self.key(self.session.player.id))
        self.session.redis.srem(self.SET_KEY, self.session.player.id)

    def all_player_ids(self):
        """
        Returns all player ids
        """
        members = self.session.redis.smembers(self.SET_KEY)
        return members

    def all_players(self):
        """
        Returns all players objects
        """
        return [self.load(id_) for id_ in self.all_player_ids()]

    def other_player_ids(self):
        """
        Returns other player ids
        """
        members = self.all_player_ids()
        other_ids = {int(m.decode()) for m in members} - {self.session.player.id}
        return other_ids

    def other_players(self):
        """
        Returns other players
        """
        return [self.load(id_) for id_ in self.other_player_ids()]

    def handle_player_died(self, args):
        player_id = args[0]
        killer_id = args[2]
        if player_id == self.session.player.id:
            self.publish_health_update([self.session.player.id], -100)
            self.publish_mana_update([self.session.player.id], -100)
            self.send_event(event=Event.SOUND_REQUEST, prepared_data=Sound(file="slinky-death.ogg"))

        if killer_id == self.session.player.id:
            self.session.player = self.session.player_cache.load(self.session.player.id)
            self.session.player.kill_count += 1
            self.session.text_message_cache.send_kill_count_increased(self.session.player.kill_count)

            new_scale = self.session.player.scale * 1.05
            if new_scale <= 3:
                self.session.player.scale = new_scale
                self.publish_scale_update(self.session.player.scale)

            new_power = self.session.player.power * 1.05
            if new_scale <= 3:
                self.session.player.power = new_power

            self.save(self.session.player)

    def publish_new_player(self, player):
        """
        Publishes new player
        """
        self.save(player)
        self.session.redis.sadd(self.SET_KEY, player.id)
        self.session.player_position_cache.update_position(player)
        self.send_event(event=Event.NEW_PLAYER_JOINED,
                        prepared_data=player)

    def publish_position_update(self, position: dict, send_to_owner: bool = False) -> PlayerPositionUpdate:
        """
        Pushes position update, only if some time passed
        """
        event_dtime = datetime.now()

        if event_dtime - self.last_position_update < timedelta(
            milliseconds=config.position_update_delay
        ) and not send_to_owner:
            # if it's a teleport we don't want to drop position updating
            return

        self.last_position_update = event_dtime
        position_update = PlayerPositionUpdate(
            **position._json(), id=self.session.player.id, send_to_owner=send_to_owner
        )

        self.session.player_position_cache.update_position(position_update)

        self.send_event(event=Event.POSITION_UPDATED,
                        prepared_data=position_update)

        return position_update

    def publish_animation_update(self, animation):
        animation_update = PlayerAnimationUpdate(
            **animation._json(), id=self.session.player.id
        )

        self.send_event(event=Event.ANIMATION_UPDATED,
                        prepared_data=animation_update)

        return animation_update

    def publish_health_update(self, targets, hp_change) -> None:
        affected_players = []

        for id_ in targets:
            try:
                player = self.load(id_)
                affected_players.append(player)
            except AssertionError:
                continue

        for player in affected_players:
            player.health = min(max((player.health - hp_change, 0)), 100)
            self.save(player)

        health_updates = [HealthUpdate(p.id, p.health) for p in affected_players]

        self.send_event(event=Event.HEALTH_UPDATED,
                        prepared_data=health_updates)

    def publish_mana_update(self, targets, mana_change) -> None:
        affected_players = []

        for id_ in targets:
            try:
                player = self.load(id_)
                affected_players.append(player)
            except AssertionError:
                continue

        for player in affected_players:
            player.mana = min(max((player.mana - mana_change, 0)), 100)
            self.save(player)

        mana_updates = [ManaUpdate(p.id, p.mana) for p in affected_players]

        self.send_event(event=Event.MANA_UPDATED,
                        prepared_data=mana_updates)

    def publish_name_update(self, name):
        self.session.player = self.load(id_=self.session.player.id)
        self.session.player.name = name
        self.save(self.session.player)
        name_update = NameUpdate(self.session.player.id,
                                 self.session.player.name)

        self.send_event(event=Event.NAME_UPDATED,
                        prepared_data=name_update)

    def publish_model_update(self, model):
        self.session.player = self.load(id_=self.session.player.id)
        self.session.player.model_id = model
        self.save(self.session.player)
        model_update = ModelUpdate(self.session.player.id,
                                   self.session.player.model_id)
        self.send_event(
            event=Event.MODEL_UPDATED,
            prepared_data=model_update
        )

    def publish_weapon_update(self, weapon_id):
        self.session.player = self.load(id_=self.session.player.id)
        self.session.player.weapon_id = weapon_id
        self.save(self.session.player)
        weapon_update = WeaponUpdate(self.session.player.id,
                                     self.session.player.weapon_id)
        self.send_event(
            event=Event.WEAPON_UPDATED,
            prepared_data=weapon_update,
        )

    def publish_disconnect(self):
        disconnection = Disconnection(self.session.player.id)
        self.send_event(
            event=Event.DISCONNECTION,
            prepared_data=disconnection
        )

    def publish_scale_update(self, new_scale):
        self.send_event(
            event=Event.SCALE_UPDATED,
            prepared_data=ScaleUpdate(id=self.session.player.id, scale=new_scale)
        )

    def send_not_enough_mana(self):
        self.send_event(
            event=Event.NOT_ENOUGH_MANA,
            prepared_data=NotEnoughMana(id=self.session.player.id)
        )

    def send_connection_check_event(self):
        self.send_event(
            event=self.CONNECTION_CHECK_EVENT,
            prepared_data=None
        )

    def subscribe_connection_check(self, subscriber):
        """
        Creates a thread that will subscribe to the channel
        specific for current user
        """
        self.accept_event(
            event=self.CONNECTION_CHECK_EVENT,
            handler=subscriber
        )