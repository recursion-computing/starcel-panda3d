from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task


class NodeControl:
    def __init__(self, node, parent_node):
        self.controlled_node = node
        self.controlling_node = parent_node.attach_new_node("actor control node")
        self.controlling_node.set_pos(node.get_pos(parent_node))
        self.controlling_node.set_hpr(node.get_hpr(parent_node))
        self.controlled_node.reparent_to(self.controlling_node)
        self.controlled_node.set_pos(0, 0, 0)
        self.controlled_node.set_hpr(0, 0, 0)
        self.movement_speed = 2.8

    def move_forward(self, task):
        self.controlling_node.set_y(
            self.controlling_node, -self.movement_speed * globalClock.getDt()
        )
        self.controlled_node.set_h(0)
        return Task.cont

    def move_backward(self, task):
        self.controlling_node.set_y(
            self.controlling_node, self.movement_speed * globalClock.getDt()
        )
        self.controlled_node.set_h(180)
        return Task.cont

    def move_left(self, task):
        self.controlling_node.set_x(
            self.controlling_node, self.movement_speed * 0.7 * globalClock.getDt()
        )
        self.controlled_node.set_h(90)
        return Task.cont

    def move_right(self, task):
        self.controlling_node.set_x(
            self.controlling_node, -self.movement_speed * 0.7 * globalClock.getDt()
        )
        self.controlled_node.set_h(-90)
        return Task.cont

    def rotate_left(self, task):
        self.controlling_node.set_h(
            self.controlling_node, self.movement_speed * 80 * globalClock.getDt()
        )
        return Task.cont

    def rotate_right(self, task):
        self.controlling_node.set_h(
            self.controlling_node, -self.movement_speed * 80 * globalClock.getDt()
        )
        return Task.cont

    def rotate_by_angle(self, angle):
        self.controlling_node.set_h(self.controlling_node.get_h() + angle)

    def adjust_rotation_to_camera(self, cam_ctrl):
        rel_hook_hpr = cam_ctrl.hook.get_hpr(self.controlling_node.get_parent())
        self.controlling_node.set_h(rel_hook_hpr.get_x())
        cam_ctrl.hook.set_hpr(self.controlling_node.get_parent(), rel_hook_hpr)
