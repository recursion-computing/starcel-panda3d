from ..domain import SpellUpdate
from server.event.event_user import EventUser
import json
import dataclasses
from datetime import datetime, timedelta
import logging
from server.event.event import Event

log = logging.getLogger(__name__)


class SpellCache(EventUser):
    HMSET_PREFIX = "player_trigger_times_"
    GLOBAL_COOLDOWN = 1
    COOLDOWN_TIME_PER_SPELL_ID = {
        0: 1.0,
        1: 2.0,
        2: 3.0,
        3: 4.0
    }

    def __init__(self, session):
        super().__init__()
        self.session = session
        self.temp_cooldown_per_id = {
            0: 1.0,
            1: 2.0,
            2: 3.0,
            3: 4.0
        }

    def key(self):
        """
        Prefixed key for dict of trigger times.
        """
        return f"{self.HMSET_PREFIX}{self.session.player.id}"

    def publish_combat_data(self, combat_data):
        self.send_event(event=Event.COMBAT_DATA_CREATED,
                        prepared_data=combat_data)

    def initialize_trigger_times(self) -> None:
        """
        Initialize spell trigger in redis.
        """
        min_time = datetime.now().timestamp()
        trigger_times = {
            0: min_time,
            1: min_time,
            2: min_time,
            3: min_time
        }
        self.store_trigger_times(trigger_times)

    def store_trigger_times(self, trigger_times: dict) -> None:
        """
        Save trigger times dict in redis.
        """
        self.session.redis.hmset(self.key(), trigger_times)

    def load_trigger_times(self) -> dict:
        """
        Loads trigger times dict from redis.
        """
        dict_ = self.session.redis.hgetall(self.key())
        decoded_dict_ = {int(k.decode()): float(v.decode()) for k, v in dict_.items()}
        return decoded_dict_

    def trigger_spell_cooldown(self, spell_id: int) -> None:
        """
        Updates trigger time of the spell.
        """
        times = self.load_trigger_times()
        assert spell_id in times, spell_id
        self.trigger_global_cooldown(times)
        times[spell_id] = datetime.now().timestamp()
        self.temp_cooldown_per_id[spell_id] = self.COOLDOWN_TIME_PER_SPELL_ID[spell_id]
        self.store_trigger_times(times)

    def trigger_global_cooldown(self, times: dict) -> None:
        now = datetime.now()
        for spell_id, trigger_time in times.items():
            trigger_time = datetime.fromtimestamp(trigger_time)
            cooldown_elapsed = now - trigger_time
            remaining_time = timedelta(seconds=self.temp_cooldown_per_id[spell_id]) - cooldown_elapsed
            if remaining_time < timedelta(seconds=self.GLOBAL_COOLDOWN):
                self.temp_cooldown_per_id[spell_id] = self.GLOBAL_COOLDOWN
                times[spell_id] = now.timestamp()

    def is_spell_ready(self, spell_id: int) -> None:
        times = self.load_trigger_times()
        trigger_time = times.get(spell_id)
        trigger_time = datetime.fromtimestamp(trigger_time)
        if trigger_time is None:
            return False
        return datetime.now() - trigger_time > timedelta(seconds=self.temp_cooldown_per_id[spell_id])
