from .model.model import MainSectionModel
from .scene.scene import MainSectionScene
from .control.control import Control
from .ui.ui import MainSectionUi
from ..base import Section
from protocol.domain.WorldState import WorldState
from client.local import core
from .model.node_watcher import NodeWatcher


class MainSection(Section):
    def __init__(self):
        self.model = MainSectionModel()
        self.scene = MainSectionScene(self.model)
        self.ui = MainSectionUi(self.model)
        self.control = None

    def show(self) -> None:
        self.scene.show()
        self.ui.show()

    def hide(self) -> None:
        self.scene.hide()
        self.ui.hide()

    def load_model(self, model: WorldState) -> None:
        self.model.load(model)

    def post_model_setup(self) -> None:
        units = self.model.units_by_id.values()
        for unit in units:
            self.scene.manipulator.spawn_unit(unit)
            self.ui.floating_bars.create_bar(unit)
        self.enable_control()
        NodeWatcher(self.model.player_unit.base_node, self.scene.node, 0).enable()

    def enable_control(self) -> None:
        player_unit = self.model.units_by_id[self.model.player_id]
        self.control = Control(player_unit, core.instance.camera)
        self.control.enable(self.scene.node)

    def disable_control(self) -> None:
        pass
