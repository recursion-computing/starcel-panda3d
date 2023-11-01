from client.local.model import static_model


class WeaponModelBank:
    model_by_id = {
        0: static_model.Antaras,
        1: static_model.Fiera,
        2: static_model.Flugel,
        3: static_model.IgusBlade
    }

    @classmethod
    def get_by_id(cls, weapon_id):
        assert weapon_id in cls.model_by_id, f"Weapon ID {weapon_id} doesn't exist."
        return cls.model_by_id[weapon_id]
