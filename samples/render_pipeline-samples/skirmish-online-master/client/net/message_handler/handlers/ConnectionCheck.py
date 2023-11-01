from .base import MessageHandler
from protocol import messages


class ConnectionCheckHandler(MessageHandler):
    handled_message = messages.ConnectionCheckResponse
    response_message = messages.ConnectionCheckRequest
    # request is a message from the client and response is a message from client
    # in this case server sends the message first (checking if client is still connected)

    def handle_message(self):
        pass

    def __call__(self):
        return messages.ConnectionCheckRequest()
