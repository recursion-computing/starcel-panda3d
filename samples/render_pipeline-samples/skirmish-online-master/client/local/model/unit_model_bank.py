from client.local.model import actor


class UnitModelBank:
    model_by_id = {
        0: actor.DarkElf,
        1: actor.Elf,
        2: actor.Kamael,
        3: actor.Dwarf
    }

    @classmethod
    def get_by_id(cls, model_id):
        assert model_id in cls.model_by_id, f"Model ID {model_id} doesn't exist."
        return cls.model_by_id[model_id]


