from .base import ConfiguredActor
from client.local.animation import Stand, Run, MeleeAttack1, MeleeAttack2, MagicAttack1


class DarkElf(ConfiguredActor):

    MODEL_PATH = "local/assets/characters/dark-elf.gltf"
    HEIGHT = 0.55
    ANIMATION_MAPPING = {
        Stand(): "wait_2HS_FDarkElf",
        Run(): "run_2HS_FDarkElf",
        MeleeAttack1(): "Atk01_2HS_FDarkElf",
        MeleeAttack2(): "SpAtk001_2HS_FDarkElf",
        MagicAttack1(): "CastMid_FDarkElf",
    }


    def configure(self):
        self.set_play_rate(3, self.ANIMATION_MAPPING[MeleeAttack1()])
        self.set_play_rate(2, self.ANIMATION_MAPPING[MeleeAttack2()])
        self.set_play_rate(3, self.ANIMATION_MAPPING[MagicAttack1()])

