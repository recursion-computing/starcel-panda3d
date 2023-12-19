from panda3d.core import ModifierButtons, Vec3, PStatClient, Point3, CurveFitter, KeyboardButton, Quat,LVecBase3f, NodePath, LRotation
from starcelfuncs import FiniteRepetitionSelector, look_at_rotation, Cylinder
from DistributedSmoothActor import DistributedSmoothActor
import random
import numpy as np


class DroneController():
    def __init__(self, client_repository):
        #base = showbase
        self.movement = [0, 0, 0]
        self.velocity = Vec3(0.0)
        self.hpr_movement = [0, 0]
        self.speed = 1
        self.initial_position = Vec3(0)
        self.initial_destination = Vec3(0)
        self.initial_hpr = Vec3(0)
        self.mouse_enabled = True
        self.last_mouse_pos = [0, 0]
        self.mouse_sensivity = 4
        self.keyboard_hpr_speed = 1
        self.use_hpr = False
        self.smoothness = .0001
        # self.bobbing_amount = 1.5
        # self.bobbing_speed = 0.5

        self.client_repository = client_repository
        self.mmb_activated = False
        # self.alt_activated = False
        # self.ctrl_activated = False
        self.shift_activated = False
        self.ctrl_activated = False
        self.size = 1
        self.freelook_activated = False
        self.freelook_distance = 8
        self.drone = DistributedSmoothActor(self.client_repository)
        #self.boom_arm = Cylinder((0,0,0),(-2,0,0),0.1,self.drone)

        self.boom_pivot = NodePath('boom_pivot')
        self.cam_point = NodePath('cam_point')
        self.boom_pivot.reparent_to(render)
        self.cam_point.reparent_to(self.boom_pivot)

        self.value_selector = FiniteRepetitionSelector("*", 2)

        self.client_repository.createDistributedObject(distObj=self.drone, zoneId=2)

        # mouseWatcherNode actually also handles keyboard
        # self.isDown = base.mouseWatcherNode.is_button_down

        # base.accept("alt", self.alt_down)
        # base.accept("alt-up", self.alt_up)
        # base.accept("ctrl", self.ctrl_down)
        # base.accept("ctrl-up", self.ctrl_up)

        self.drone.start()
        self.drone.hide()


    def set_initial_position(self, pos, target):
        """ Sets the initial camera position """
        self.initial_position = pos
        self.initial_destination = target
        self.use_hpr = False
        self.reset_to_initial()

    def set_initial_position_hpr(self, pos, hpr):
        """ Sets the initial camera position """
        self.initial_position = pos
        self.initial_hpr = hpr
        self.use_hpr = True
        self.reset_to_initial()

    def set_scale(self, size):
        self.size = size
        self.drone.setScale(self.size)

    def reset_to_initial(self):
        """ Resets the camera to the initial position """
        base.camera.set_pos(self.initial_position)

        if self.use_hpr:
            base.camera.set_hpr(self.initial_hpr)
        else:
            base.camera.look_at(
                self.initial_destination.x, self.initial_destination.y,
                self.initial_destination.z)

    def set_movement(self, direction, amount):
        self.movement[direction] = amount

    def set_hpr_movement(self, direction, amount):
        self.hpr_movement[direction] = amount

    def alt_down(self):
        self.freelook_activated = True

    def alt_up(self):
        self.freelook_activated = False

    def ctrl_down(self):
        self.ctrl_activated = True

    def ctrl_up(self):
        self.ctrl_activated = False

    def shift_down(self):
        self.shift_activated = True

    def shift_up(self):
        self.shift_activated = False

    def wheel_up(self):
        if self.ctrl_activated:
            self.ctrl_wheel_up()
        else:
            if self.freelook_activated:
                self.alt_wheel_up()
            if self.shift_activated:
                self.shift_wheel_up()

    def wheel_down(self):
        if self.ctrl_activated:
            self.ctrl_wheel_down()
        else:
            if self.freelook_activated:
                self.alt_wheel_down()
            if self.shift_activated:
                self.shift_wheel_down()

    def ctrl_wheel_up(self):
        self.size = self.value_selector.increase_value(self.size)
        self.set_scale(self.size)

    def ctrl_wheel_down(self):
        self.size = self.value_selector.decrease_value(self.size)
        self.set_scale(self.size)

    def alt_wheel_up(self):
        self.freelook_distance = self.value_selector.decrease_value(self.freelook_distance)

    def alt_wheel_down(self):
        self.freelook_distance = self.value_selector.increase_value(self.freelook_distance)

    def shift_wheel_up(self):
        self.speed = self.value_selector.increase_value(self.speed)

    def shift_wheel_down(self):
        self.speed = self.value_selector.decrease_value(self.speed)

    def mmb_down(self):
        self.mmb_activated = True

    def mmb_up(self):
        self.mmb_activated = False

    def unbind(self):
        """ Unbinds the movement controler and restores the previous state """
        raise NotImplementedError()

    @property
    def clock_obj(self):
        return base.taskMgr.globalClock

    def setup(self):
        """ Attaches the movement controller and inits the keybindings """
        # x
        base.accept("raw-w", self.set_movement, [0, 1])
        base.accept("raw-w-up", self.set_movement, [0, 0])
        base.accept("raw-s", self.set_movement, [0, -1])
        base.accept("raw-s-up", self.set_movement, [0, 0])

        # y
        base.accept("raw-a", self.set_movement, [1, -1])
        base.accept("raw-a-up", self.set_movement, [1, 0])
        base.accept("raw-d", self.set_movement, [1, 1])
        base.accept("raw-d-up", self.set_movement, [1, 0])

        # z
        base.accept("raw-e", self.set_movement, [2, 1])
        base.accept("raw-e-up", self.set_movement, [2, 0])
        base.accept("raw-q", self.set_movement, [2, -1])
        base.accept("raw-q-up", self.set_movement, [2, 0])

        # wireframe + debug + buffer viewer
        # base.accept("f3", base.toggle_wireframe)
        # base.accept("f11", lambda: base.win.save_screenshot("screenshot.png"))
        # base.accept("j", self.print_position)

        # mouse
        # base.accept("mouse1", self.set_mouse_enabled, [True])
        # base.accept("mouse1-up", self.set_mouse_enabled, [False])

        # arrow mouse navigation
        # base.accept("arrow_up", self.set_hpr_movement, [1, 1])
        # base.accept("arrow_up-up", self.set_hpr_movement, [1, 0])
        # base.accept("arrow_down", self.set_hpr_movement, [1, -1])
        # base.accept("arrow_down-up", self.set_hpr_movement, [1, 0])
        # base.accept("arrow_left", self.set_hpr_movement, [0, 1])
        # base.accept("arrow_left-up", self.set_hpr_movement, [0, 0])
        # base.accept("arrow_right", self.set_hpr_movement, [0, -1])
        # base.accept("arrow_right-up", self.set_hpr_movement, [0, 0])

        # Alt freelook scroll
        base.accept("mouse2", self.mmb_down)
        base.accept("mouse2-up", self.mmb_up)
        base.accept("control", self.ctrl_down)
        base.accept("control-up", self.ctrl_up)
        base.accept("alt", self.alt_down)
        base.accept("alt-up", self.alt_up)
        base.accept("shift", self.shift_down)
        base.accept("shift-up", self.shift_up)
        base.accept("wheel_down", self.wheel_down)
        base.accept("wheel_up", self.wheel_up)
        # base.accept("alt-wheel_up", self.alt_wheel_up)
        # base.accept("alt-wheel_down", self.alt_wheel_down)
        # base.accept("shift-wheel_up", self.shift_wheel_up)
        # base.accept("shift-wheel_down", self.shift_wheel_down)


        # disable modifier buttons to be able to move while pressing shift for example
        base.mouseWatcherNode.set_modifier_buttons(ModifierButtons())
        base.buttonThrowers[0].node().set_modifier_buttons(ModifierButtons())

        # disable pandas builtin mouse control
        base.disableMouse()

        # add yourself as an update task which gets executed very early before the rendering
        self.update_task = base.addTask(self.update, "UpdateDroneController", sort=-40)

        # # Hotkeys to connect to pstats and reset the initial position
        # base.accept("1", PStatClient.connect)
        # base.accept("3", self.reset_to_initial)

    def print_position(self):
        """ Prints the camera position and hpr """
        pos = base.cam.get_pos(base.render)
        hpr = base.cam.get_hpr(base.render)
        print("(Vec3({}, {}, {}), Vec3({}, {}, {})),".format(
            pos.x, pos.y, pos.z, hpr.x, hpr.y, hpr.z))

    def update(self, task):
        """ Internal update method """
        delta = self.clock_obj.get_dt()

        # Update mouse first
        if base.mouseWatcherNode.has_mouse():
            x = base.mouseWatcherNode.get_mouse_x()
            y = base.mouseWatcherNode.get_mouse_y()
            self.current_mouse_pos = (x * base.camLens.get_fov().x * self.mouse_sensivity,
                                      y * base.camLens.get_fov().y * self.mouse_sensivity)

            if self.mouse_enabled:
                diffx = -self.current_mouse_pos[0] # TODO: FIX with M_relative in 11.0 (self.last_mouse_pos[0] - self.current_mouse_pos[0])
                diffy = self.current_mouse_pos[1]  # (self.last_mouse_pos[1] - self.current_mouse_pos[1])
                # print(diffx)
                # print(diffy)

                # Don't move in the very beginning TODO: FIX with M_relative in 11.0
                # if self.last_mouse_pos[0] == 0 and self.last_mouse_pos[1] == 0:
                #     diffx = 0
                #     diffy = 0
                #             if self.mmb_activated:
                #                 base.camera.setR(base.camera.getR() + x * rot_speed)
                #                 self.drone.setR(base.camera.getR())
                #             else:
                #                 base.camera.setH(base.camera.getH() + -x * rot_speed)
                #                 self.drone.setH(base.camera.getH() - 180)

                if self.freelook_activated:
                    self.boom_pivot.set_pos(self.drone.get_pos())
                    if self.mmb_activated:
                        self.boom_pivot.setR(self.drone.get_r() - diffx)
                    else:
                        self.boom_pivot.setH(self.drone.get_h() + diffx)
                        self.boom_pivot.setP(self.drone.get_p() + diffy)
                    # if self.mmb_activated:
                    #     self.boom_pivot.setR(self.drone, -diffx)
                    # else:
                    #     self.boom_pivot.setH(self.drone, diffx)
                    #     self.boom_pivot.setP(self.drone, diffy)
                    self.cam_point.set_pos((0,-self.freelook_distance, 0))

                    # self.boom_arm.update((0,0,0), np.array([-self.freelook_distance, 0, 0]),.1)

                    # self.drone.getPos(),np.array([self.freelook_distance,0,0]),.1) #self.drone.getPos(), np.array(self.drone.getPos()) + np.array([0,self.freelook_distance,0]), 1)

                    base.camera.setPos(render.getRelativePoint(self.boom_pivot, self.cam_point.get_pos()))

                    base.camera.look_at(self.drone.get_pos())
                    self.drone.show()

                else:
                    self.boom_pivot.set_hpr(0,0,0) # hpr = ypr
                    self.drone.hide()

                    base.camera.set_pos(self.drone.get_pos())
                    # if self.mmb_activated:
                    #     self.drone.setR(self.drone.get_r() - diffx)
                    # else:
                    #     self.drone.setH(self.drone.get_h() + diffx)
                    #     self.drone.setP(self.drone.get_p() - diffy)

                    if self.mmb_activated:
                        self.drone.setR(self.drone, -diffx)
                    else:
                        self.drone.setH(self.drone, diffx)
                        self.drone.setP(self.drone, diffy)
                    base.camera.set_quat(self.drone.get_quat())


                    # quat = LRotation((0,0,0),0)
                    # if self.mmb_activated:
                    #     quat *= LRotation((1, 0, 0),self.drone.get_r() -diffx)
                    # else:
                    #     quat *= LRotation((0, 0, 1), self.drone.get_h() + diffx)
                    #     quat *= LRotation((0, 1, 0), self.drone.get_p() - diffy)

                    # self.drone.set_quat(quat)
                    # base.camera.set_quat(quat)

                    # if self.mmb_activated:
                    #     #TODO: FIX
                    #     self.drone.setR(self.drone.get_r() - diffx)
                    #     base.camera.set_r(self.drone.getR())
                    # else:
                    #     self.drone.setH(self.drone.get_h() + diffx)
                    #     base.camera.set_h(self.drone.getH())
                    #     self.drone.setP(self.drone.get_p() - diffy)
                    #     base.camera.set_p(self.drone.getP())

                    self.last_mouse_pos = self.current_mouse_pos[:]
                    base.win.movePointer(0, int(base.win.getXSize() / 2), int(base.win.getYSize() / 2))

                    # Compute movement in render space
                    movement_direction = (Vec3(self.movement[1], self.movement[0], self.movement[2]) * self.speed * delta * 100.0)

                    # transform by the camera direction
                    camera_quaternion = base.camera.get_quat(base.render)
                    translated_direction = camera_quaternion.xform(movement_direction)

                    # # z-force is independent of camera direction
                    # translated_direction.add_z(
                    #      * delta * 120.0 * self.speed)

                    self.velocity += translated_direction # * 0.15

                    # apply the new position
                    base.camera.set_pos(base.camera.get_pos() + self.velocity)
                    self.drone.setPos(base.camera.getPos())

                    # test2 = tuple(np.array([2*random.random() -1, 2*random.random() -1, 2*random.random() -1, 2*random.random() -1])*.00001)
                    # rotation_quat = Quat(test2)
                    # base.camera.set_quat(base.camera, rotation_quat)

                    # transform rotation (keyboard keys)
                    # rotation_speed = self.keyboard_hpr_speed * 100.0
                    # rotation_speed *= delta
                    # base.camera.set_hpr(
                    #     base.camera.get_hpr() + Vec3(
                    #         self.hpr_movement[0], self.hpr_movement[1], 0) * rotation_speed)

                    # fade out velocity
                    self.velocity = self.velocity * max(0.0, 1.0 - delta * 60.0 / max(0.001, self.smoothness))

        # bobbing
        # ftime = self.clock_obj.get_frame_time()
        # rotation = (ftime % self.bobbing_speed) / self.bobbing_speed
        # rotation = (min(rotation, 1.0 - rotation) * 2.0 - 0.5) * 2.0
        # if self.velocity.length_squared() > 1e-5 and self.speed > 1e-5:
        #     rotation *= self.bobbing_amount
        #     rotation *= min(1, self.velocity.length()) / self.speed * 0.5
        # else:
        #     rotation = 0
        # base.camera.set_r(rotation)
        return task.cont

    def play_motion_path(self, points, point_duration=1.2):
        """ Plays a motion path from the given set of points """
        fitter = CurveFitter()
        for i, (pos, hpr) in enumerate(points):
            fitter.add_xyz_hpr(i, pos, hpr)

        fitter.compute_tangents(1.0)
        curve = fitter.make_hermite()
        print("Starting motion path with", len(points), "CVs")

        base.render2d.hide()
        base.aspect2d.hide()

        self.curve = curve
        self.curve_time_start = self.clock_obj.get_frame_time()
        self.curve_time_end = self.clock_obj.get_frame_time() + len(points) * point_duration
        self.delta_time_sum = 0.0
        self.delta_time_count = 0
        base.addTask(self.camera_motion_update, "RP_CameraMotionPath", sort=-50)
        base.taskMgr.remove(self.update_task)

    def camera_motion_update(self, task):
        if self.clock_obj.get_frame_time() > self.curve_time_end:
            print("Camera motion path finished")

            # Print performance stats
            avg_ms = self.delta_time_sum / self.delta_time_count
            print("Average frame time (ms): {:4.1f}".format(avg_ms * 1000.0))
            print("Average frame rate: {:4.1f}".format(1.0 / avg_ms))

            self.update_task = base.addTask(
                self.update, "RP_UpdateMovementController", sort=-50)
            base.render2d.show()
            base.aspect2d.show()
            return task.done

        lerp = (self.clock_obj.get_frame_time() - self.curve_time_start) /\
            (self.curve_time_end - self.curve_time_start)
        lerp *= self.curve.get_max_t()

        pos, hpr = Point3(0), Vec3(0)
        self.curve.evaluate_xyz(lerp, pos)
        self.curve.evaluate_hpr(lerp, hpr)

        base.camera.set_pos(pos)
        base.camera.set_hpr(hpr)

        self.delta_time_sum += self.clock_obj.get_dt()
        self.delta_time_count += 1

        return task.cont




    # def wheel_up(self):
    #     pass
    #
    # def wheel_down(self):
    #     pass
    #
    # def ctrl_down(self):
    #     self.ctrl_activated = True
    #
    # def ctrl_up(self):
    #     self.ctrl_activated = False

    # def alt_down(self):
    #     self.alt_activated = True
    #     self.freelook_activated = True
    #
    # def alt_up(self):
    #     self.alt_activated = False
    #     self.freelook_activated = False
    #


    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    # def move(self, task):
    #     # Get the time that elapsed since last frame.  We multiply this with
    #     # the desired speed in order to find out with which distance to move
    #     # in order to achieve that desired speed.
    #     dt = globalClock.getDt()
    #     move_speed = 7
    #     # If a move-key is pressed, move drone in the specified direction.
    #     # if self.isDown(KeyboardButton.asciiKey(b"w")):
    #     #     self.drone.setY(self.drone, -move_speed * dt)
    #     # if self.isDown(KeyboardButton.asciiKey(b"a")):
    #     #     self.drone.setX(self.drone, move_speed * dt)
    #     # if self.isDown(KeyboardButton.asciiKey(b"s")):
    #     #     self.drone.setY(self.drone, move_speed * dt)
    #     # if self.isDown(KeyboardButton.asciiKey(b"d")):
    #     #     self.drone.setX(self.drone, -move_speed * dt)
    #     # if self.isDown(KeyboardButton.asciiKey(b"e")):
    #     #     self.drone.setZ(self.drone, move_speed * dt)
    #     # if self.isDown(KeyboardButton.asciiKey(b"q")):
    #     #     self.drone.setZ(self.drone, -move_speed * dt)
    #     # if self.isDown(KeyboardButton.ascii_key("alt")):
    #     #     print("alt clicked")
    #     if self.isDown(KeyboardButton.asciiKey(b"w")):
    #         self.drone.setPos(self.drone, render.getRelativeVector(self.drone, Vec3(0, 1, 0)) * move_speed * dt)
    #
    #     # update distributed position and rotation (TODO: func no longer available?)
    #     #self.drone.setDistPos(self.drone.getX(), self.drone.getY(), self.drone.getZ())
    #     #self.drone.setDistHpr(self.drone.getH(), self.drone.getP(), self.drone.getR())
    #
    #     if self.alt_activated:
    #         self.freelook_activated = True
    #     else:
    #         self.freelook_activated = False
    #
    #     if self.freelook_activated:
    #         self.boom_arm.update((0,0,0),np.array([self.freelook_distance,0,0]),.1) # self.drone.getPos(),np.array([self.freelook_distance,0,0]),.1)#self.drone.getPos(), np.array(self.drone.getPos()) + np.array([0,self.freelook_distance,0]), 1)
    #         #swap to freelook camera
    #         base.camera.setPos(render.getRelativePoint(self.drone, tuple(self.boom_arm.line_end)))
    #
    #         new_rot = look_at_rotation(render.getRelativePoint(self.drone, tuple(self.boom_arm.line_end)), self.drone.getPos()) # TODO: camera.lookat func?
    #
    #         if new_rot is not None and not np.isnan(new_rot).any():
    #             base.camera.setHpr(new_rot[2]+270, new_rot[1]+270, new_rot[0])
    #
    #     else:
    #         rot_speed = 60
    #         base.camera.setPos(self.drone.getPos())
    #         if base.mouseWatcherNode.hasMouse():
    #             x = base.mouseWatcherNode.getMouseX()
    #             y = base.mouseWatcherNode.getMouseY()
    #             base.camera.setP(base.camera.getP() + y * rot_speed)
    #             self.drone.setP(base.camera.getP() + 90)
    #             if self.mmb_activated:
    #                 base.camera.setR(base.camera.getR() + x * rot_speed)
    #                 self.drone.setR(base.camera.getR())
    #             else:
    #                 base.camera.setH(base.camera.getH() + -x * rot_speed)
    #                 self.drone.setH(base.camera.getH() - 180)
    #     return task.cont


