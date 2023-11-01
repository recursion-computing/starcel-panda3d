from .task_performers.health_regen import HealthRegenerator
from .task_performers.mana_regen import ManaRegenerator
from .task_performers.connection_checker import ConnectionChecker
from server.event.event_user import EventUser


class SessionTaskManager:
    """
    Creates, runs and stores all task performers for the specified connection/session.
    """
    def __init__(self, session, connection, server):
        self.session = session
        self.connection = connection
        self.server = server
        self.task_performers = [
            HealthRegenerator(session, connection, server),
            ConnectionChecker(session, connection, server),
            ManaRegenerator(session, connection, server)
        ]
        for task_performer in self.task_performers:
            task_performer.start_task()

    def stop_tasks(self):
        for performer in self.task_performers:
            performer._continue = False


