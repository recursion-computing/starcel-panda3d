from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages


class CombatDataHandler(MessageHandler):
    handled_message = messages.CombatDataResponse
    response_message = None

    def handle_message(self):
        data = self.message.data
        core.instance.messenger.send(
            Event.COMBAT_DATA_RECEIVED,
            sentArgs=[data.spell, data.hp_change, data.source, data.targets.data],
        )
