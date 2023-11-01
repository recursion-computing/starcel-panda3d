from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages


class NotEnoughManaHandler(MessageHandler):
    handled_message = messages.NotEnoughMana
    response_message = None

    def handle_message(self):
        core.instance.messenger.send(
            Event.NOT_ENOUGH_MANA,
            sentArgs=[None],
        )
