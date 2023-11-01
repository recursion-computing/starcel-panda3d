from client.local import core
from client.local.font import MainFont
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectLabel
from panda3d.core import TextNode
from client.local.section.main.ui.utils.frame import Frame
from typing import List


class TextLog(DirectObject):
    def __init__(self, parent_node, width=0.3, height=0.21, x=0, y=0, line_spacing=0.02, text_scale=0.01,
                 n_lines=9, bg_color=(1, 1, 1, 0), fg_color=(1, 1, 1, 1), text_x=0.005, text_y=0.025):
        DirectObject.__init__(self)
        self.node = parent_node.attach_new_node("text log node")
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.text_x = text_x
        self.text_y = text_y
        self.line_spacing = line_spacing
        self.text_scale = text_scale
        self.frame = Frame(parent_node=self.node,
                           color=(0, 0, 0, 0.6),
                           width=self.width,
                           height=self.height)
        self.frame.frame.set_bin('fixed', 30)
        font = MainFont()
        self.entry_node = self.node.attach_new_node("entry node")
        self.text_nodes = []
        # create node for each line of text, so it can be displaced when resizing the window
        for i in range(n_lines):
            self.text_nodes.append(self.node.attach_new_node(f"text node {i}"))
        # lines of text that are going to be displayed in the terminal
        self.lines_queue = ["" for i in range(n_lines)]
        self.direct_labels = []
        for i in range(n_lines):
            self.direct_labels.append(
                DirectLabel(
                    text=self.lines_queue[i],
                    text_align=TextNode.ALeft,
                    text_font=font,
                    text_fg=fg_color,
                    text_bg=bg_color,
                    frameColor=bg_color,
                    parent=self.text_nodes[i],
                )
            )
        self.accept("aspectRatioChanged", self.aspect_ratio_change_update)

    def get_window_size(self):
        return core.instance.win.get_x_size(), core.instance.win.get_y_size()

    def aspect_ratio_change_update(self):
        ww, wh = self.get_window_size()
        self.update_position(ww, wh)
        self.update_scale(ww, wh)

    def update_position(self, ww, wh):
        line_y = 0
        for text_node in reversed(self.text_nodes):
            # text offset in pixels
            text_x_px = self.text_x * ww
            text_y_px = (self.text_y + line_y) * wh
            text_node.set_pos(text_x_px, 0, text_y_px)
            line_y += self.line_spacing

    def update_scale(self, ww, wh):
        for text_node in reversed(self.text_nodes):
            text_node.set_scale(self.text_scale * ww)

    def add_line(self, line):
        self._add_lines(self.split_into_smaller_lines(line, chars_per_line=54))

    def _add_lines(self, lines):
        """
        :param lines: array of lines to be added
        """
        for line in lines:
            self.lines_queue.append(line)
            self.lines_queue.pop(0)

    def split_into_smaller_lines(self, string: str, chars_per_line: int) -> List[str]:
        return [string[i:i+chars_per_line] for i in range(0, len(string), chars_per_line)]

    def update_view(self):
        for i, direct_label in enumerate(self.direct_labels):
            direct_label["text"] = self.lines_queue[i]
