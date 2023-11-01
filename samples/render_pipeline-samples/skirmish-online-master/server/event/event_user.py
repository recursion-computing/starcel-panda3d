from redis import Redis
import logging
from server.event.dispatcher import Dispatcher
from server import config

log = logging.getLogger(__name__)


class EventUser:
    """
    Inherit from this class if you want to send or listen to events.
    """
    USE_REDIS_PUBSUB = config.use_redis_pubsub

    def __init__(self, host=config.redis_host):
        self.redis = Redis(host=host)
        self.listening_threads = []

    def stop_listening_threads(self):
        """
        Make sure to stop the listening threads.
        """
        count = len(self.listening_threads)
        for thread in self.listening_threads:
            thread.stop()

    def accept_event(self, event, handler, sleep_time=0.25):
        """
        Spawn a thread that will listen for specified event from redis.
        """
        if self.USE_REDIS_PUBSUB:
            p = self.redis.pubsub()
            p.subscribe(**{event: handler})
            thread = p.run_in_thread(sleep_time=sleep_time)
            self.listening_threads.append(thread)
            return thread
        else:
            Dispatcher.register_handler(event=event, handler=handler)

    def send_event(self, event, prepared_data):
        """
        Publish event in redis.
        """
        if self.USE_REDIS_PUBSUB:
            self.redis.publish(event, prepared_data)
        else:
            Dispatcher.dispatch_event(event=event, event_data=prepared_data)
