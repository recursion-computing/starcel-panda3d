from protocol.domain.base import BaseModel


class Section:
    """
    Sections are different parts of application, having different views (scene, GUI) and model.
    """

    def show(self) -> None:
        pass

    def hide(self) -> None:
        pass

    def load_model(self, model: BaseModel) -> None:
        pass

    def post_model_setup(self) -> None:
        """
        Called after loading the model.
        """
        pass
