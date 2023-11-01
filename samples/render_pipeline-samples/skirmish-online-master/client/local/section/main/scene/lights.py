from panda3d.core import PointLight, AmbientLight
from client.local import core


class Lights:
    def __init__(self, node):
        self.node = node

        plight = PointLight("plight")
        plight.setColor((5, 5, 5, 0))
        plight_node_path = self.node.attachNewNode(plight)
        plight_node_path.setPos(20, 0, 0)
        core.instance.render.setLight(plight_node_path)

        alight = AmbientLight("alight")
        alight.setColor((1, 1, 1, 0))
        alight_node_path = self.node.attachNewNode(alight)
        alight_node_path.setPos(20, 0, 0)
        core.instance.render.setLight(alight_node_path)
