from .base import ConfiguredActor
from client.local.animation import Stand, Run, MeleeAttack1, MeleeAttack2, MagicAttack1


class Dwarf(ConfiguredActor):

    MODEL_PATH = "local/assets/characters/dwarf-f.gltf"
    HEIGHT = 0.5
    ANIMATION_MAPPING = {
        Stand(): "wait_2HS_FDwarf",
        Run(): "run_2HS_FDwarf",
        MeleeAttack1(): "Atk01_2HS_FDwarf",
        MeleeAttack2(): "SpAtk001_2HS_FDwarf",
        MagicAttack1(): "CastMid_A_FDwarf",
    }

    def configure(self):
        self.set_play_rate(0.2, self.ANIMATION_MAPPING[Stand()])
        self.set_play_rate(3, self.ANIMATION_MAPPING[MeleeAttack1()])
        self.set_play_rate(2, self.ANIMATION_MAPPING[MeleeAttack2()])
        self.set_play_rate(3, self.ANIMATION_MAPPING[MagicAttack1()])

