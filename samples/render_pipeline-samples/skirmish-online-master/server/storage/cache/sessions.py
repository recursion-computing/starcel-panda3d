import logging


log = logging.getLogger(__name__)


class SessionCache:
    SET_KEY = "sessions"
    PREFIX = "session_"

    def __init__(self, session):
        self.session = session

    @property
    def key(self):
        """
        Prefixed key for session
        """
        return f"{self.PREFIX}{self.session.id}"

    def store(self):
        """
        Store session
        """
        self.session.redis.sadd(self.SET_KEY, self.session.id)
        self.session.redis.set(self.key, self.session.dump())

    def get_other_sessions(self):
        """
        Returns all other session ids
        """
        members = self.session.redis.smembers(self.SET_KEY)
        return {m.decode() for m in members} - {self.session.id}

    def get_all_sessions(self):
        """
        Returns all other session ids
        """
        members = self.session.redis.smembers(self.SET_KEY)
        return {m.decode() for m in members}
