from ..model.model import MainSectionModel
from client.local import core

from .skybox import Skybox
from .terrain import Terrain
from .lights import Lights

from .actor_manipulation.manipulator import ActorManipulator


class MainSectionScene:
    def __init__(self, model: MainSectionModel):
        self.model = model
        self.node = core.instance.render.attach_new_node("main-section-node")
        self.terrain = Terrain(self.node)
        self.lights = Lights(self.node)
        self.skybox = Skybox(self.node)
        self.manipulator = ActorManipulator(self.model, self.node)

    def show(self) -> None:
        self.node.show()

    def hide(self) -> None:
        self.node.hide()
