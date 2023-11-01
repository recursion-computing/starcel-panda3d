from .base import ConfiguredActor
from client.local.animation import Stand, Run, MeleeAttack1, MeleeAttack2, MagicAttack1


class Kamael(ConfiguredActor):

    MODEL_PATH = "local/assets/characters/kamael.gltf"
    HEIGHT = 0.57
    ANIMATION_MAPPING = {
        Stand(): "wait_2HS_MKamael",
        Run(): "run_2HS_MKamael",
        MeleeAttack1(): "Atk01_2HS_MKamael",
        MeleeAttack2(): "SpAtk001_2HS_MKamael",
        MagicAttack1(): "CASTmid_D_MKamael",
    }

    def configure(self):
        self.set_play_rate(3, self.ANIMATION_MAPPING[MeleeAttack1()])
        self.set_play_rate(3, self.ANIMATION_MAPPING[MeleeAttack2()])
        self.set_play_rate(3, self.ANIMATION_MAPPING[MagicAttack1()])
