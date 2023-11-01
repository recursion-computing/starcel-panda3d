from panda3d.core import Vec3


class CameraControl:
    def __init__(self, camera):
        self.camera = camera
        self.hook = None
        self.zoom_speed = 0.2
        self.max_distance = 10
        self.min_distance = 1.5
        self.low_vert_limit = -10
        self.upp_vert_limit = 90
        self.rotate_with_character = True

    def attach_to(self, node, pos):
        self.hook = node.attach_new_node("camera_hook")
        self.hook.set_pos(pos)
        self.hook.set_hpr(0, 0, 0)
        self.camera.reparent_to(self.hook)
        self.camera.set_pos(0, 0, 0)
        self.camera.set_hpr(-180, 0, 0)

    def zoom_in(self, amount):
        camera_direction = self.camera.get_parent().get_relative_vector(
            self.camera, Vec3.forward()
        )
        new_pos = self.camera.get_pos() + camera_direction * self.zoom_speed * amount

        if new_pos.length() < self.min_distance:
            self.camera.set_pos(-camera_direction * self.min_distance)
        elif new_pos.length() >= 0 and new_pos.get_y() >= 0:
            self.camera.set_pos(new_pos)

    def zoom_out(self, amount):
        camera_direction = self.camera.get_parent().get_relative_vector(
            self.camera, Vec3.forward()
        )
        new_pos = self.camera.get_pos() - camera_direction * self.zoom_speed * amount
        if new_pos.length() < self.max_distance:
            self.camera.set_pos(new_pos)
        else:
            self.camera.set_pos(-camera_direction * self.max_distance)

    def move_on_horizontal_orbit(self, angle):
        self.hook.set_h(self.hook.get_h() + angle)

    def move_on_vertical_orbit(self, angle):
        new_angle = self.hook.get_p() + angle
        if new_angle > self.upp_vert_limit:
            self.hook.set_p(90)
        elif new_angle < self.low_vert_limit:
            self.hook.set_p(-10)
        else:
            self.hook.set_p(new_angle)
