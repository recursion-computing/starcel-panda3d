from panda3d.core import NodePath
from client.local import core
from abc import abstractmethod


class StaticModelBase(NodePath):
    """
    Enhanced NodePath for static models that includes path for the model.
    """
    MODEL_PATH: str = None

    def __new__(cls):
        return core.instance.loader.load_model(cls.MODEL_PATH)

