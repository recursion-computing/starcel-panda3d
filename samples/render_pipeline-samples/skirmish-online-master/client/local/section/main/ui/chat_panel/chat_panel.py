from direct.showbase.DirectObject import DirectObject
from .chat_log import ChatLog
from client.local import core
from .chat_input import ChatInput


class ChatPanel(DirectObject):
    """
    Interface panel used for displaying chat & other messages from the server
    + text input for sending messages to server.
    """

    def __init__(self, parent_node, x=0.02, y=0.02):
        super().__init__()
        self.node = parent_node.attach_new_node("chat panel node")
        self.log = ChatLog(parent_node=self.node)
        self.input = ChatInput(parent_node=self.node)
        self.accept("aspectRatioChanged", self.aspect_ratio_change_update)
        self.x = x
        self.y = y

    def get_window_size(self):
        return core.instance.win.get_x_size(), core.instance.win.get_y_size()

    def aspect_ratio_change_update(self):
        ww, wh = self.get_window_size()
        x_px = self.x * ww
        y_px = self.y * wh
        self.node.set_pos(x_px, 0, -wh + y_px)
