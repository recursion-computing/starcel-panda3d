from .base import ConfiguredActor
from client.local.animation import Stand, Run, MeleeAttack1, MeleeAttack2, MagicAttack1


class Elf(ConfiguredActor):

    MODEL_PATH = "local/assets/characters/elf.gltf"
    HEIGHT = 0.53
    ANIMATION_MAPPING = {
        Stand(): "wait_2HS_FElf",
        Run(): "run_2HS_FElf",
        MeleeAttack1(): "Atk02_2HS_FElf",
        MeleeAttack2(): "SpAtk001_2HS_FElf",
        MagicAttack1(): "CastMid_FElf",
    }

    def configure(self):
        self.set_play_rate(0.2, self.ANIMATION_MAPPING[Stand()])
        self.set_play_rate(3, self.ANIMATION_MAPPING[MeleeAttack1()])
        self.set_play_rate(2, self.ANIMATION_MAPPING[MeleeAttack2()])
        self.set_play_rate(3, self.ANIMATION_MAPPING[MagicAttack1()])
