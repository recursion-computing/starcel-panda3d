from .handlers.bank import TextCommandHandlerBank


class TextCommandHandler:
    def __init__(self, session, command_vector):
        self.command_vector = command_vector
        self.session = session

    def __call__(self):
        keyword = self.command_vector[0]
        handler_cls = TextCommandHandlerBank.by_keyword(keyword)
        handler_cls(self.session, self.command_vector)()

    @staticmethod
    def is_a_command(word_vector: list[str]) -> bool:
        keyword = word_vector[0]
        handler_cls = TextCommandHandlerBank.by_keyword(keyword)
        return handler_cls is not None



