from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectWaitBar
from client.local import core


class WaitBar(DirectObject):
    """
    Wrapper for DirectWaitBar that scales/moves accordingly to the window size (for Pixel2d root).
    """
    def __init__(self, parent):
        super().__init__()
        self.node = parent.attach_new_node("cooldown bar")
        self.wait_bar = DirectWaitBar(
            value=0,
            scale=1,
            parent=self.node,
            frameColor=(0, 0, 0, 0.3),
            barColor=(1, 1, 0, 0.6),
        )
        self.width = 0.026
        self.height = 0.005
        self.accept("aspectRatioChanged", self.aspect_ratio_change_update)

    def aspect_ratio_change_update(self):
        """
        Rescale/move wait-bar when the window size has changed.
        """

        reference_width = core.instance.win.get_x_size()
        reference_height = core.instance.win.get_y_size()
        width_px = reference_width * self.width
        height_px = reference_height * self.height
        self.wait_bar["frameSize"] = (
            0,
            width_px,
            height_px,
            0,
        )
        self.wait_bar.set_pos(reference_width * -0.026, 0, 0)