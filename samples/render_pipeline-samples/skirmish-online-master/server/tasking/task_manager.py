from .session_task_manager import SessionTaskManager
from server.event.event_user import EventUser
from server.event.event import Event


class TaskManager(EventUser):
    """
    Creates and stores all task managers per session/connection.
    """
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.session_task_managers = {}
        self.accept_event(
            event=Event.CLIENT_DISCONNECTION_PUBLISHED,
            handler=self.handle_client_disconnection_published
        )

    def new_session_task_manager(self, session, connection):
        self.session_task_managers[connection] = SessionTaskManager(session, connection, self.server)

    def handle_client_disconnection_published(self, connection):
        session_task_mgr = self.session_task_managers[connection]
        session_task_mgr.stop_tasks()
        del self.session_task_managers[connection]


