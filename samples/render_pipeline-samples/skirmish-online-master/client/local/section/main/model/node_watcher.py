from direct.task.Task import Task
from client.event import Event
from panda3d.core import NodePath
from client.local import core
from datetime import datetime, timedelta


class NodeWatcher:
    TASK_PREFIX = "NODE_WATCHER_"

    def __init__(self, node: NodePath, reference_node: NodePath, watcher_id):
        self.last_notify_time = datetime.now()
        self.notify_min_interval = timedelta(milliseconds=100)

        self.node = node
        self.reference_node = reference_node
        self.id_ = watcher_id

        self.last_pos = None
        self.last_rot = None

    def enable(self) -> None:
        core.instance.task_mgr.add(
            self.send_new_position_events, f"{NodeWatcher.TASK_PREFIX}{self.id_}"
        )

    def disable(self) -> None:
        core.instance.task_mgr.remove(f"{NodeWatcher.TASK_PREFIX}{self.id_}")

    def send_new_position_events(self, task):
        curr_pos = self.node.get_pos(self.reference_node)
        curr_rot = self.node.get_hpr(self.reference_node)

        now = datetime.now()
        if now - self.last_notify_time < self.notify_min_interval:
            return Task.cont

        send_event = False
        if curr_pos != self.last_pos:
            self.last_pos = curr_pos
            send_event = True
        if curr_rot != self.last_rot:
            self.last_rot = curr_rot
            send_event = True
        if send_event:
            self.last_notify_time = now
            pos_rot = [value for value in self.last_pos] + [
                value for value in self.last_rot
            ]
            core.instance.messenger.send(Event.MY_POS_ROT_CHANGED, sentArgs=[pos_rot])
        return Task.cont
