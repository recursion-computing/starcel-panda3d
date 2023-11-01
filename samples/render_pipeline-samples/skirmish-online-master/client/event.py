class Event:
    """
    Panda3D framework represents events as strings.
    """

    # raw data about unit received from server
    # -----------------------------------------------
    NEW_UNIT_DATA_RECEIVED = "new-unit-data-received"
    UNIT_POS_ROT_RECEIVED = "unit-pos-rot-received"
    UNIT_ANIMATION_RECEIVED = "unit-animation-received"
    UNIT_HEALTH_RECEIVED = "unit-health-received"
    UNIT_MANA_RECEIVED = "unit-mana-received"
    UNIT_NAME_RECEIVED = "unit-name-received"
    UNIT_MODEL_RECEIVED = "unit-model-received"
    UNIT_WEAPON_RECEIVED = "unit-weapon-received"
    UNIT_SCALE_RECEIVED = "unit-scale-received"
    UNIT_DISCONNECTED = "unit-disconnected"
    NOT_ENOUGH_MANA = "not-enough-mana"  # concerns only this client
    # -----------------------------------------------

    # other data received from server
    # -----------------------------------------------
    MSG_RECEIVED = "msg-received"
    COMBAT_DATA_RECEIVED = "combat-data-received"
    TRIGGER_COOLDOWN_RECEIVED = "trigger-cooldown-received"
    SET_SPELL_RECEIVED = "set-spell-received"
    # -----------------------------------------------

    # local unit updates, they pass unit reference as one of event args
    # -----------------------------------------------
    NEW_UNIT_CREATED = "new-unit-created"
    UNIT_HP_UPDATED = "unit-hp-updated"
    UNIT_MANA_UPDATED = "unit-mana-updated"
    UNIT_NAME_UPDATED = "unit-name-updated"
    UNIT_POS_ROT_UPDATED = "unit-pos-rot-updated"
    UNIT_ANIMATION_UPDATED = "unit-animation-updated"
    UNIT_MODEL_UPDATED = "unit-model-updated"
    UNIT_WEAPON_UPDATED = "unit-weapon-updated"
    UNIT_SCALE_UPDATED = "unit-scale-updated"
    # -----------------------------------------------

    # local events
    # -----------------------------------------------
    MY_ANIMATION_CHANGE_ATTEMPT = "my-animation-change-attempt"
    MY_POS_ROT_CHANGED = "my-pos-rot-changed"
    MY_SPELL_ATTEMPT = "my-spell-attempt"
    COMMAND_TO_SERVER_ENTERED = "local-command-to-server-entered"
    COMBAT_DATA_PARSED = "combat-data-parsed"
    UNIT_DELETED = "unit-deleted"
    # -----------------------------------------------
