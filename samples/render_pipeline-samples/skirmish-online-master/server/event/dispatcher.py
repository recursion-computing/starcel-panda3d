from typing import Callable


class Dispatcher:
    HANDLERS_BY_EVENT = {}

    @classmethod
    def register_handler(cls, event: str, handler: Callable):
        handlers = cls.HANDLERS_BY_EVENT.get(event)
        if handlers is None:
            cls.HANDLERS_BY_EVENT[event] = [handler]
        else:
            handlers.append(handler)

    @classmethod
    def dispatch_event(cls, event: str, event_data):
        handlers = cls.HANDLERS_BY_EVENT.get(event)
        if handlers is None:
            return
        for handler in handlers:
            handler(event_data)
