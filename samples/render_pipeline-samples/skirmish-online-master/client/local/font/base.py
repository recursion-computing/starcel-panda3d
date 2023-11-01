from panda3d.core import TextFont
from client.local import core


class FontBase:
    FONT_PATH: str = None
    """
    Panda3D font with specified font path.
    """
    def __new__(cls):
        font = core.instance.loader.load_font(cls.FONT_PATH)
        return font
