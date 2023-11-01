from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages

import logging


log = logging.getLogger(__name__)


class SetWeaponHandler(MessageHandler):
    handled_message = messages.WeaponUpdateMessage
    response_message = None

    def handle_message(self):
        data = self.message.data
        core.instance.messenger.send(
            Event.UNIT_WEAPON_RECEIVED,
            sentArgs=[data.id, data.weapon_id],
        )
