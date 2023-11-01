from ...storage.domain.combat_data import CombatData
from protocol.domain import Spells, AnimationName, Animation
from .bank import MetaClass
from server.event.event_user import EventUser
from server.event.event import Event
from typing import List
import logging
import random

log = logging.getLogger(__name__)


class BaseSpellHandler(EventUser, metaclass=MetaClass):
    SPELL: Spells = None
    ANIMATION: AnimationName = None
    LOOP: int = 0
    MANA_COST: int = 0
    DAMAGE_RANGE: tuple = (0, 10)
    AOE_RANGE: float = 0.4

    def __init__(self, session, spell_data):
        """
        Stores session and spell data
        """
        EventUser.__init__(self)
        self.session = session
        self.spell_data = spell_data

    def __call__(self) -> CombatData:
        """
        Main method. It does several things:
            1. publish_spell_update
            2. calculate_targets
            3. interact with targets
            4. produce response
        """
        self.session.player = self.session.player_cache.load(self.session.player.id)
        if not self.valid():
            return
        if not self.session.spell_cache.is_spell_ready(self.spell_data.spell):
            return self.produce_response([], 0)
        if not self.session.player.mana >= self.MANA_COST:
            self.session.player_cache.send_not_enough_mana()
            return

        self.session.spell_cache.trigger_spell_cooldown(self.spell_data.spell)

        targets_ids = self.calculate_targets()
        hp_change = self.calculate_damage(targets_ids) * self.session.player.power
        combat_data = self.produce_response(targets_ids, hp_change)

        self.publish_health_update(targets_ids, hp_change)
        self.publish_mana_update([self.session.player.id], self.MANA_COST)
        self.publish_animation_update()
        self.publish_combat_data(combat_data)

        players = [self.session.player_cache.load(target_id) for target_id in targets_ids]

        self.session.player_cache.save(self.session.player)
        for player in players:
            if player.health <= 0:
                self.send_event(event=Event.PLAYER_DIED, prepared_data=(player.id,
                                                                        self.session.player.name,
                                                                        self.session.player.id))

    def valid(self) -> bool:
        """
        If spell is valid
        """
        return True

    def publish_animation_update(self):
        """
        Notifies all other players about
        new animation
        """
        self.session.set_animation(
            Animation(animation_name=self.ANIMATION.value, loop=self.LOOP),
        )

    def publish_health_update(self, targets, hp_change):
        """
        Notifies all other players about
        health updates
        """
        self.session.player_cache.publish_health_update(
            targets,
            hp_change,
        )

    def publish_mana_update(self, targets, mana_change):
        self.session.player_cache.publish_mana_update(
            targets,
            mana_change
        )

    def publish_combat_data(self, combat_data):
        self.session.spell_cache.publish_combat_data(
            combat_data
        )

    def calculate_targets(self) -> List[int]:
        """
        Calculates targets
        """
        return self.session.player_position_cache.get_nearby(
            self.session.player,
            self.AOE_RANGE * self.session.player.power,
            self.AOE_RANGE * self.session.player.power,
            self.AOE_RANGE * self.session.player.power,
        )

    def calculate_damage(self, targets: List[int]) -> int:
        """
        Calculates damage for targets
        """
        return random.randint(self.DAMAGE_RANGE[0], self.DAMAGE_RANGE[1])

    def produce_response(self, targets: List[int], hp_change: int) -> CombatData:
        """
        Produces response
        """
        return CombatData(
            spell=self.spell_data.spell,
            hp_change=hp_change,
            source=self.session.player.id,
            targets=targets,
        )

    def teleport_player_to_random_place(self, player_id):
        pass
