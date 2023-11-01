from client.local import core
from client.local.model.static_model import Arena


class Terrain:
    def __init__(self, node):
        self.node = node
        terrain = Arena()
        terrain.reparent_to(self.node)
        terrain.set_scale(10)
        terrain.set_z(0.82)
