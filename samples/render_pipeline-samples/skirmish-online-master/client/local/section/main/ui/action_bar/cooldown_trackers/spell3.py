from .base import CooldownTrackerBase


class TrackerSpell3(CooldownTrackerBase):
    ICON = "local/assets/spell-icons/spell-icon3.png"
    DEFAULT_COOLDOWN = 3
    KEY_EVENT = "r"
    DISPLAYED_TEXT = "R"
