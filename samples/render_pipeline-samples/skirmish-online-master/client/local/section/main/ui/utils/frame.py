from client.local import core
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectFrame
from client.local.font import MainFont


class Frame(DirectObject):
    """
    Wrapper for DirectFrame that scales/moves accordingly to the window size (for Pixel2d root).
    """
    def __init__(self, parent_node, color=(0, 0, 0, 1), width=0.5, height=0.5, x=0, y=0, image=None, hpr=(0, 0, 0),
                 image_hpr=(0, 0, 0), text=""):
        DirectObject.__init__(self)
        self.node = parent_node.attach_new_node(f"frame {self}")
        self.text_x_offset = 0.004
        self.text_y_offset = 0.016
        self.text_scale = 0.01
        self.frame = DirectFrame(
            hpr=hpr,
            parent=self.node,
            frameColor=color,
            frameTexture=image,
            image_hpr=image_hpr,
            text=text,
            text_roll=180,
            text_scale=20,
            text_font=MainFont(),
            text_fg=(1, 1, 1, 1),
        )
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.accept("aspectRatioChanged", self.aspect_ratio_change_update)

    def aspect_ratio_change_update(self):
        """
        Rescale/move frame when the window size has changed.
        """

        reference_width = core.instance.win.get_x_size()
        reference_height = core.instance.win.get_y_size()

        center = reference_width / 2
        width_px = reference_width * self.width
        height_px = reference_height * self.height
        self.frame["frameSize"] = (
            0,
            width_px,
            height_px,
            0,
        )
        self.frame["text_pos"] = (reference_width * self.text_x_offset, reference_height * self.text_y_offset, 0)
        self.frame["text_scale"] = reference_width * self.text_scale

        x_px = reference_width * self.x
        y_px = reference_height * self.y

        self.node.set_pos(x_px, 0, y_px)

    def get_x_size(self):
        return self.frame["frameSize"][1]

    def get_y_size(self):
        return self.frame["frameSize"][2]



