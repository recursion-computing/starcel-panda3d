from .base import MessageHandler
from protocol import messages


class AnimationHandler(MessageHandler):
    handled_message = messages.AnimationRequest
    response_message = None

    def handle_message(self):
        animation_data = self.message.data
        self.session.set_animation(animation_data)
