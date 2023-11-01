from direct.actor.Actor import Actor
from client.local.animation.base import AnimationBase
from client.local.animation.Run import Run
from client.local.animation.MagicAttack1 import MagicAttack1
from client.local.animation.MeleeAttack2 import MeleeAttack2
from client.local.animation.MeleeAttack1 import MeleeAttack1
from abc import abstractmethod
from client.local import core
import warnings


class ConfiguredActor(Actor):
    """
    Enhanced Panda3D Actor with additional configuration for specific animated models.
    """
    MODEL_PATH: str = None
    HEIGHT: float = None
    ANIMATION_MAPPING: dict = {}
    """
    Connects animation names in universal format with their embedded names (for this specified model).
    """

    def __init__(self):
        super().__init__(self.MODEL_PATH)
        self.REVERSE_ANIMATION_MAPPING = {v: k for k, v in self.ANIMATION_MAPPING.items()}
        """
        Connects embedded names with their universal names.
        """
        self.configure()
        # quickly before 21.07.2022 test doing it here
        self.walk_sound = core.instance.loader.load_sfx("client/local/assets/sounds/metal-walk.ogg")
        self.hit_sound = core.instance.loader.load_sfx("client/local/assets/sounds/oof2.ogg")

    def play_anim_uf(self, animation: AnimationBase) -> None:
        """
        Play animation specified in universal format.
        """
        embedded = self.ANIMATION_MAPPING.get(animation)
        if embedded is None:
            warnings.warn(f"Actor {type(self).__name__} doesn't support animation {animation}.")
            return
        if isinstance(animation, Run):
            self.walk_sound.set_loop(True)
            self.walk_sound.play()
        else:
            self.walk_sound.stop()

        if isinstance(animation, MagicAttack1) or isinstance(animation, MeleeAttack1) or isinstance(animation, MeleeAttack2):
            self.hit_sound.play()

        if animation.LOOP:
            self.loop(embedded)
        else:
            self.play(embedded)

    def get_current_anim_uf(self) -> AnimationBase:
        """
        Get current animation string in universal format.
        """
        current_embedded = self.get_current_anim()
        return self.REVERSE_ANIMATION_MAPPING.get(current_embedded)


    @abstractmethod
    def configure(self) -> None:
        pass
