from ..model.model import MainSectionModel
from client.local import core
from .dmg_text import DmgText
from .combat_log.combat_log_panel import CombatLogPanel
from .floating_bars import FloatingBars
from .chat_bubbles import ChatBubbles
from .action_bar.action_bar import ActionBar
from .chat_panel.chat_panel import ChatPanel


class MainSectionUi:
    def __init__(self, model: MainSectionModel):
        self.model = model
        self.node = core.instance.pixel2d.attach_new_node("interface node")
        self.chat_panel = ChatPanel(parent_node=self.node)
        self.combat_log = CombatLogPanel(parent_node=self.node, units=self.model.units_by_id)
        self.action_bar = ActionBar(self.node)

        # UI that is reparented to 3D elements
        self.chat_bubbles = ChatBubbles(self.model)
        self.floating_bars = FloatingBars(self.model)
        self.dmg_text = DmgText(self.model)

    def show(self) -> None:
        self.node.show()

    def hide(self) -> None:
        self.node.hide()
