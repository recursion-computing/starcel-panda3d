from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath
from gltf.viewer import App

from .loader import load_actor


class Loader(object):
    def load_model(self, file_path, **kw):
        return NodePath(load_actor(file_path))

    def destroy(self):
        pass


def noop(*args, **kw):
    pass


class KApp(App):
    def __init__(self):
        # init ShowBase and prevent it from spawning twice
        ShowBase.__init__(self)
        ShowBase.__init__ = noop

        self.loader = Loader()
        super().__init__()


def main():
    KApp().run()


if __name__ == '__main__':
    main()
