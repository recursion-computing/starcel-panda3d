from .combat_log import CombatLog
from client.local import core
from direct.showbase.DirectObject import DirectObject


class CombatLogPanel(DirectObject):
    def __init__(self, parent_node, units, x=0.02, y=0.02):
        super().__init__()
        self.node = parent_node.attach_new_node("combat log panel")
        self.log = CombatLog(parent_node=self.node, units=units)
        self.x = x
        self.y = y
        self.accept("aspectRatioChanged", self.aspect_ratio_change_update)

    def get_window_size(self):
        return core.instance.win.get_x_size(), core.instance.win.get_y_size()

    def aspect_ratio_change_update(self):
        ww, wh = self.get_window_size()
        self.update_position(ww, wh)

    def update_position(self, ww, wh):
        ww, wh = self.get_window_size()
        log_width_px = self.log.width * ww
        x_offset_px = self.x * ww
        x_px = ww - x_offset_px - log_width_px
        y_px = self.y * wh
        self.node.set_pos(x_px, 0, -wh + y_px)
