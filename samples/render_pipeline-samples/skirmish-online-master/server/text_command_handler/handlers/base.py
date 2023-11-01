from .bank import MetaClass
from abc import abstractmethod
from server.event.event_user import EventUser
import logging

log = logging.getLogger(__name__)


class BaseTextCommandHandler(EventUser, metaclass=MetaClass):
    KEYWORD: str = None
    # number of words in a command, for example "/setname Grzesiek" has 2
    LENGTH: int = 2

    def __init__(self, session, command_vector: list[str]):
        EventUser.__init__(self)
        self.session = session
        self.command_vector = command_vector

    def __call__(self):
        if self.is_command_valid():
            self.handle_command()

    @abstractmethod
    def handle_command(self):
        pass

    def is_command_valid(self):
        return len(self.command_vector) > self.LENGTH

