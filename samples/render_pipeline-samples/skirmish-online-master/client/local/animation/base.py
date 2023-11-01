class AnimationBase(str):
    """
    Animations in panda3d are represented with strings.
    This is an enhanced string with some additional animation parameters.
    """
    ANIMATION_STR: str = None
    IMPORTANCE: int = 0
    LOOP: bool = False

    def __new__(cls):
        obj = super().__new__(cls, cls.ANIMATION_STR)
        return obj
