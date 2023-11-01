from client.local.animation import Run, Stand, MagicAttack1, MeleeAttack1, MeleeAttack2


class AnimationBank:
    animation_by_str = {
        "stand": Stand(),
        "run": Run(),
        "melee_attack_1": MeleeAttack1(),
        "melee_attack_2": MeleeAttack2(),
        "magic_attack_1": MagicAttack1()
    }

    @classmethod
    def get_animation_by_string(cls, string):
        assert string in cls.animation_by_str, f"Animation {string} not found"
        return cls.animation_by_str[string]