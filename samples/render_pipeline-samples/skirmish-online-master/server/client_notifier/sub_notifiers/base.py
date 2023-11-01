from protocol.messages.base import Message
from server.event.event_user import EventUser
from server.event.event import Event
import logging

log = logging.getLogger(__name__)


class SubNotifierBase(EventUser):
    """
    Sub-notifiers listen for their assigned event and notify client about it.
    """
    EVENT: Event = None
    MESSAGE: Message = None
    DROP_FOR_SELF: bool = False
    """
    Set it to true of you don't want to notify user about data concerning them.
    """
    DROP_FOR_OTHERS: bool = False
    """
    Set it to true if you want to notify user only about data concerning them.
    """

    def __init__(self, event_notifier):
        """
        Notifies user about some game event.
        """
        super().__init__()
        self.event_notifier = event_notifier

    def __call__(self, data):
        """
        Handle event by notifying user.
        """
        if self.DROP_FOR_SELF and self.message_is_about_this_player(data):
            return
        if self.DROP_FOR_OTHERS and not self.message_is_about_this_player(data):
            return
        if self.drop(data):
            return
        self.update_cache(data)
        self.event_notifier.notify(
            self.MESSAGE.build(data),
        )

    def start_listening(self):
        """
        Start listening for event.
        """
        self.accept_event(event=self.EVENT,
                          handler=self)

    def message_is_about_this_player(self, data):
        return self.event_notifier.session.player is not None and data.id == self.event_notifier.session.player.id

    def drop(self, data) -> bool:
        """
        Add some custom check if needed. Return False if you don't want to continue sending this message.
        """

    def update_cache(self, data):
        """
        Update session's cache if needed.
        """
        pass

    def test(self):
        pass
