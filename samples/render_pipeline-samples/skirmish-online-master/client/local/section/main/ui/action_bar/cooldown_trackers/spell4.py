from .base import CooldownTrackerBase


class TrackerSpell4(CooldownTrackerBase):
    ICON = "local/assets/spell-icons/spell-icon4.png"
    DEFAULT_COOLDOWN = 4
    KEY_EVENT = "f"
    DISPLAYED_TEXT = "F"
