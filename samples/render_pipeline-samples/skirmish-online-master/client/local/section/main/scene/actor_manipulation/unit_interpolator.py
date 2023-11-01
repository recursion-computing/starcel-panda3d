from panda3d.direct import SmoothMover
from direct.showbase.ShowBaseGlobal import globalClock


class UnitInterpolator:
    def __init__(self, unit):
        self.unit = unit
        self.smooth_mover = SmoothMover()
        self.smooth_mover.set_smooth_mode(SmoothMover.SM_on)

    def update(self):
        self.smooth_mover.setPos(self.unit.x, self.unit.y, self.unit.z)
        self.smooth_mover.setHpr(self.unit.h, self.unit.p, self.unit.r)
        self.smooth_mover.setTimestamp(globalClock.get_frame_time())
        self.smooth_mover.markPosition()

    def interpolate(self):
        self.smooth_mover.compute_and_apply_smooth_pos_hpr(
            self.unit.base_node, self.unit.base_node
        )
