from .base import MessageHandler
from client.event import Event
from client.local import core
from protocol import messages


class AnimationMessageHandler(MessageHandler):
    handled_message = messages.AnimationResponse
    response_message = None

    def handle_message(self):
        data = self.message.data
        id_, anim_name, loop = data.id, data.animation_name, data.loop
        core.instance.messenger.send(
            Event.UNIT_ANIMATION_RECEIVED, sentArgs=[id_, anim_name, loop]
        )
