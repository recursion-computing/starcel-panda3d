from client.local import core
from client.local.section.main.control.camera_control import CameraControl
from client.local.section.main.control.node_control import NodeControl
from client.event import Event
from client.local import animation
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from panda3d.core import WindowProperties, Vec3

import datetime


class Control(DirectObject):
    def __init__(self, unit, camera):
        super().__init__()
        self.actor_control = None
        self.camera_control = None
        self.mouse_sensitivity = 0.5

        self.unit = unit
        self.camera = camera

        # input states
        self.mouse_1_clicked = False
        self.mouse_3_clicked = False
        self.w_pressed = False
        self.a_pressed = False
        self.d_pressed = False
        self.last_mouse_x = 200
        self.last_mouse_y = 200
        self.mouse_1_click_time = 0

        # assignment of handling functions
        self.event_handler_mapping = {
            "w": self.w_handler,
            "w-up": self.w_up_handler,
            "s": self.s_handler,
            "s-up": self.s_up_handler,
            "a": self.a_handler,
            "a-up": self.a_up_handler,
            "d": self.d_handler,
            "d-up": self.d_up_handler,
            "mouse1": self.mouse_1_handler,
            "mouse1-up": self.mouse_1_up_handler,
            "mouse3": self.mouse_3_handler,
            "mouse3-up": self.mouse_3_up_handler,
            "wheel_up": self.wheel_up_handler,
            "wheel_down": self.wheel_down_handler,
            "q": self.q_handler,
            "q-up": self.q_up_handler,
            "e": self.e_handler,
            "e-up": self.e_up_handler,
            "r": self.r_handler,
            "f": self.f_handler,
            "c": self.c_handler,
            "escape": self.esc_handler,
        }
        core.instance.disable_mouse()

    def enable(self, scene_node):
        if self.actor_control is None:
            self.actor_control = NodeControl(self.unit.base_node, scene_node)
        if self.camera_control is None:
            self.camera_control = CameraControl(self.camera)
            self.camera_control.attach_to(
                self.actor_control.controlling_node, Vec3(0, 0, 0.5)
            )
            self.camera_control.zoom_out(10)
        for event, handler in self.event_handler_mapping.items():
            self.accept(event, handler)

    def disable(self):
        for event, handler in self.event_handler_mapping.items():
            self.ignore(event)

    def w_handler(self):
        self.w_pressed = True
        core.instance.taskMgr.remove("MoveBackward")
        # Start moving if the character is not moving yet (mouse buttons allow to move, so we have to check).
        if not core.instance.taskMgr.hasTaskNamed("MoveForward"):
            core.instance.taskMgr.add(self.actor_control.move_forward, "MoveForward")
        self.update_animation()

    def w_up_handler(self):
        self.w_pressed = False
        # stop moving if not both mouse buttons are clicked
        if not (self.mouse_1_clicked and self.mouse_3_clicked):
            core.instance.taskMgr.remove("MoveForward")
        self.update_animation()

    def s_handler(self):
        # stop moving forward
        core.instance.taskMgr.remove("MoveForward")
        # start moving backward
        core.instance.taskMgr.add(self.actor_control.move_backward, "MoveBackward")
        self.update_animation()

    def s_up_handler(self):
        # stop moving backward
        core.instance.taskMgr.remove("MoveBackward")
        self.update_animation()

    def a_handler(self):
        self.a_pressed = True
        # stop rotating to the right
        core.instance.taskMgr.remove("RotateRight")
        core.instance.taskMgr.remove("MoveRight")

        # if the mouse3 button is clicked, start moving(!) to the left
        if self.mouse_3_clicked:
            core.instance.taskMgr.add(self.actor_control.move_left, "MoveLeft")
        # else, start rotating(!) to the left
        else:
            core.instance.taskMgr.add(self.actor_control.rotate_left, "RotateLeft")

        self.update_animation()

    def a_up_handler(self):
        self.a_pressed = False

        # stop moving/rotating to the left
        core.instance.taskMgr.remove("RotateLeft")
        core.instance.taskMgr.remove("MoveLeft")
        self.update_animation()

    def d_handler(self):
        self.d_pressed = True

        # stop moving/rotating to the right
        core.instance.taskMgr.remove("RotateLeft")
        core.instance.taskMgr.remove("MoveLeft")

        # if the mouse3 button is clicked, start moving(!) to the right
        if self.mouse_3_clicked:
            core.instance.taskMgr.add(self.actor_control.move_right, "MoveRight")
        # else, start rotating(!) to the right
        else:
            core.instance.taskMgr.add(self.actor_control.rotate_right, "RotateRight")
        self.update_animation()

    def d_up_handler(self):
        self.d_pressed = False

        # stop moving/rotating to the right
        core.instance.taskMgr.remove("RotateRight")
        core.instance.taskMgr.remove("MoveRight")
        self.update_animation()

    def mouse_1_handler(self):
        self.mouse_1_clicked = True
        self.mouse_1_click_time = datetime.datetime.now()

        # run the dragging handler
        core.instance.taskMgr.add(self.handle_m1_dragging_task, "M1Drag")

        # start moving forward if both mouse buttons are clicked and 'w' wasn't already pressed
        if self.mouse_3_clicked and not self.w_pressed:
            core.instance.taskMgr.add(self.actor_control.move_forward, "MoveForward")

        # hide the cursor
        self.set_cursor_hidden(True)

        # remember the position of mouse click
        md = core.instance.win.get_pointer(0)
        self.last_mouse_x = md.get_x()
        self.last_mouse_y = md.get_y()
        self.update_animation()

    def mouse_1_up_handler(self):
        self.mouse_1_clicked = False

        core.instance.win.move_pointer(
            0, int(self.last_mouse_x), int(self.last_mouse_y)
        )

        # show the cursor if neither of mouse buttons are clicked
        if not self.mouse_3_clicked:
            self.set_cursor_hidden(False)

        # stop moving forward in case both mouse buttons were clicked, but 'w' is still being pressed
        if not self.w_pressed:
            core.instance.taskMgr.remove("MoveForward")
        self.update_animation()

    def mouse_3_handler(self):
        self.mouse_3_clicked = True
        core.instance.taskMgr.add(self.handle_m3_dragging_task, "M3Drag")

        # adjust the controlled character's rotation to the camera
        self.actor_control.adjust_rotation_to_camera(self.camera_control)

        # move forward if both mouse buttons are clicked
        if self.mouse_1_clicked:
            if not core.instance.taskMgr.hasTaskNamed("MoveForward"):
                core.instance.taskMgr.add(
                    self.actor_control.move_forward, "MoveForward"
                )

        # switch to moving from rotating
        if self.d_pressed:
            core.instance.taskMgr.remove("RotateRight")
            core.instance.taskMgr.add(self.actor_control.move_right, "MoveRight")
        if self.a_pressed:
            core.instance.taskMgr.remove("RotateLeft")
            core.instance.taskMgr.add(self.actor_control.move_left, "MoveLeft")

        # hide the mouse
        self.set_cursor_hidden(True)

        # remember the position of mouse click
        md = core.instance.win.get_pointer(0)
        self.last_mouse_x = md.get_x()
        self.last_mouse_y = md.get_y()
        self.update_animation()

    def mouse_3_up_handler(self):
        self.mouse_3_clicked = False

        # switch from moving to rotating
        if self.d_pressed:
            core.instance.taskMgr.remove("MoveRight")
            core.instance.taskMgr.add(self.actor_control.rotate_right, "RotateRight")
        if self.a_pressed:
            core.instance.taskMgr.remove("MoveLeft")
            core.instance.taskMgr.add(self.actor_control.rotate_left, "RotateLeft")

        core.instance.win.move_pointer(
            0, int(self.last_mouse_x), int(self.last_mouse_y)
        )
        # show the cursor if neither of mouse buttons are clicked
        if not self.mouse_1_clicked:
            self.set_cursor_hidden(False)

        # stop moving forward in case both mouse buttons were clicked, but 'w' is still being pressed
        if not self.w_pressed:
            core.instance.taskMgr.remove("MoveForward")
        self.update_animation()

    def wheel_up_handler(self):
        self.camera_control.zoom_in(1)

    def wheel_down_handler(self):
        self.camera_control.zoom_out(1)

    def q_handler(self):
        core.instance.messenger.send(event=Event.MY_SPELL_ATTEMPT, sentArgs=[0])

    def q_up_handler(self):
        pass

    def e_handler(self):
        core.instance.messenger.send(event=Event.MY_SPELL_ATTEMPT, sentArgs=[1])

    def e_up_handler(self):
        pass

    def r_handler(self):
        core.instance.messenger.send(event=Event.MY_SPELL_ATTEMPT, sentArgs=[2])

    def f_handler(self):
        core.instance.messenger.send(event=Event.MY_SPELL_ATTEMPT, sentArgs=[3])

    def c_handler(self):
        pass
        # core.instance.messenger.send(event=Event.MY_SPELL_ATTEMPT, sentArgs=[4])

    def esc_handler(self):
        pass

    def handle_m1_dragging_task(self, task):
        # move the camera on the character's "orbit" only if the first button of the mouse is clicked
        if (
            core.instance.mouseWatcherNode.hasMouse()
            and self.mouse_1_clicked
            and not self.mouse_3_clicked
        ):
            self.camera_control.rotate_with_character = False
            md = core.instance.win.getPointer(0)
            delta_x = md.get_x() - self.last_mouse_x
            delta_y = md.get_y() - self.last_mouse_y
            core.instance.win.movePointer(
                0, int(self.last_mouse_x), int(self.last_mouse_y)
            )
            self.camera_control.move_on_horizontal_orbit(
                -delta_x * 0.3 * self.mouse_sensitivity
            )
            self.camera_control.move_on_vertical_orbit(
                delta_y * 0.3 * self.mouse_sensitivity
            )
        elif not self.mouse_1_clicked:
            self.camera_control.rotate_with_character = True
            return Task.done
        return Task.cont

    def handle_m3_dragging_task(self, task):
        # rotate the player if the third mouse button is clicked
        if core.instance.mouseWatcherNode.hasMouse() and self.mouse_3_clicked:
            md = core.instance.win.getPointer(0)
            delta_x = md.get_x() - self.last_mouse_x
            core.instance.win.movePointer(
                0, int(self.last_mouse_x), int(self.last_mouse_y)
            )
            self.actor_control.rotate_by_angle(-0.3 * self.mouse_sensitivity * delta_x)
        elif not self.mouse_3_clicked:
            return Task.done
        return Task.cont

    def set_cursor_hidden(self, value):
        props = WindowProperties()
        props.setCursorHidden(value)
        core.instance.win.requestProperties(props)

    def update_animation(self):
        f = core.instance.task_mgr.hasTaskNamed
        if f("MoveRight") or f("MoveLeft") or f("MoveForward") or f("MoveBackward"):
            if self.unit.actor.get_current_anim_uf() != animation.Run():
                core.instance.messenger.send(
                    event=Event.MY_ANIMATION_CHANGE_ATTEMPT, sentArgs=[animation.Run(), 1]
                )
        else:
            if self.unit.actor.get_current_anim_uf() != animation.Stand():
                core.instance.messenger.send(
                    event=Event.MY_ANIMATION_CHANGE_ATTEMPT,
                    sentArgs=[animation.Stand(), 1],
                )
