from .base import CooldownTrackerBase


class TrackerSpell1(CooldownTrackerBase):
    ICON = "local/assets/spell-icons/spell-icon1.png"
    DEFAULT_COOLDOWN = 1
    KEY_EVENT = "q"
    DISPLAYED_TEXT = "Q"
