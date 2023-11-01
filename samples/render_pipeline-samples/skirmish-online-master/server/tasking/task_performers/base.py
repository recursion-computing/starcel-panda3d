from abc import abstractmethod
from threading import Thread
from time import sleep


class TaskPerformerBase:
    INTERVAL: int = 5

    def __init__(self, session, connection, server):
        self.session = session
        self.connection = connection
        self.server = server
        self.thread = None
        self._continue = True

    @abstractmethod
    def task_tick(self):
        pass

    def perform_task(self):
        while self._continue:
            sleep(self.INTERVAL)
            self.task_tick()

    def stop_task_thread(self):
        pass
        # self.thread.stop()

    def start_task(self):
        """
        Runs a thread in which the task is performed regularly, with specified interval.
        """
        self.thread = Thread(target=self.perform_task, daemon=True)
        self.thread.start()
