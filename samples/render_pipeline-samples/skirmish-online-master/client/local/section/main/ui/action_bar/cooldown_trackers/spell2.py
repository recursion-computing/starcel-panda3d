from .base import CooldownTrackerBase


class TrackerSpell2(CooldownTrackerBase):
    ICON = "local/assets/spell-icons/spell-icon2.png"
    DEFAULT_COOLDOWN = 2
    KEY_EVENT = "e"
    DISPLAYED_TEXT = "E"
