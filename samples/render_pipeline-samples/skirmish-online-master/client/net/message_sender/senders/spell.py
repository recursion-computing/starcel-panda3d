from .base import BaseSender
from client.event import Event
from protocol.messages import SpellRequest


class SpellSender(BaseSender):
    """
    Sends spell attempt
    """

    MANAGED_EVENT = Event.MY_SPELL_ATTEMPT
    MESSAGE_CLS = SpellRequest

    def handle(self, ability: int) -> None:
        """
        Sends the spell attempt
        """
        self.send(SpellRequest.build(ability))
