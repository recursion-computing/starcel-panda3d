from client.local import core
from client.local.model.static_model import SkyBox as SkyBoxModel


class Skybox:
    def __init__(self, node):
        self.node = node
        skybox = SkyBoxModel()
        skybox.set_scale(100)
        skybox.reparent_to(core.instance.camera)
        skybox.set_compass(core.instance.render)
