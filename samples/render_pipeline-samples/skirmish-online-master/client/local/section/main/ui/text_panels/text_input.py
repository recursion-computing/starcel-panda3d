from client.local import core
from client.local.font import MainFont
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectEntry, DirectLabel
from panda3d.core import TextNode
from abc import abstractmethod


class TextInput(DirectObject):
    """
    GUI element for accepting text input that resizes/moves based on the window resolution.
    """
    def __init__(self, parent_node, x=0.005, y=0.007, text_scale=0.01, input_symbol_offset=0.01, bg_color=(1, 1, 1, 0),
                 fg_color=(1, 1, 1, 1)):
        super().__init__()
        self.node = parent_node.attach_new_node("text input node")
        self.x = x
        self.y = y
        self.text_scale = text_scale
        font = MainFont()
        # font.set_pixels_per_unit(100)
        self.entry = DirectEntry(
            frameColor=bg_color,
            text_fg=fg_color,
            parent=self.node,
            entryFont=font,
            initialText="",
            width=50,
            command=self.handle_input_entered,
            suppressKeys=True,
            scale=10,
        )
        self.input_symbol_node = self.node.attach_new_node("input symbol node")
        self.input_symbol = DirectLabel(
            text=">",
            text_align=TextNode.ALeft,
            text_font=font,
            text_fg=fg_color,
            text_bg=bg_color,
            frameColor=bg_color,
            parent=self.input_symbol_node,
        )
        self.input_symbol_node.hide()
        # distance of the '>' symbol from the entry
        self.input_symbol_offset = input_symbol_offset
        self.accept("enter", self.focus_entry)
        self.accept("aspectRatioChanged", self.aspect_ratio_change_update)

    def handle_input_entered(self, text_input):
        self.input_symbol_node.hide()
        if text_input != "":
            self.entry.enterText("")
            self.entry["focus"] = False
            self.handle_input(text_input)

    @abstractmethod
    def handle_input(self, text_input):
        pass

    def focus_entry(self):
        """
        Start accepting the input.
        """
        self.input_symbol_node.show()
        self.entry["focus"] = True

    def aspect_ratio_change_update(self):
        # window width and window height
        ww, wh = self.get_window_size()
        self.update_position(ww, wh)
        self.update_scale(ww, wh)

    def get_window_size(self):
        return core.instance.win.get_x_size(), core.instance.win.get_y_size()

    def update_position(self, ww, wh):
        self.node.set_pos(
            self.x * ww,
            0,
            self.y * wh,
        )

        self.input_symbol_node.set_x(
            -self.input_symbol_offset * ww
        )

    def update_scale(self, ww, wh):
        self.entry.set_scale(self.text_scale * ww)
        self.input_symbol_node.set_scale(self.text_scale * ww)

