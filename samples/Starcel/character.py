from panda3d.core import ModifierButtons, Vec3, Point3, CurveFitter, Quat, NodePath
from ndplot import FiniteRepetitionSelector
from src.DistributedSmoothActor import DistributedSmoothActor


class DroneController():
    def __init__(self, client_repository):
        self.movement = [0, 0, 0]
        self.velocity = Vec3(0.0)
        self.hpr_movement = [0, 0]
        self.initial_destination = Vec3(0)
        self.speed = 1
        self.initial_position = Vec3(0)
        self.initial_hpr = Vec3(0)
        self.mouse_enabled = False
        self.last_mouse_pos = [0, 0]
        self.diffx = 0
        self.diffy = 0
        self.initial_diffx = 0
        self.initial_diffy = 0
        self.offset_diffx = 0
        self.offset_diffy = 0
        self.mouse_sensitivity = 4
        self.keyboard_hpr_speed = 1
        self.use_hpr = False
        self.smoothness = .0001
        # self.bobbing_amount = 1.5
        # self.bobbing_speed = 0.5

        self.render_pipeline = None
        self.client_repository = client_repository
        self.mmb_activated = False
        # self.alt_activated = False
        # self.ctrl_activated = False
        self.shift_activated = False
        self.ctrl_activated = False
        self.size = 1
        self.freelook_activated = False
        self.firstpersonlook_activated = False
        self.freelook_distance = 8
        self.current_freelook_rot_r = base.camera.get_r()
        self.drone = DistributedSmoothActor(self.client_repository)
        self.keyboard_capturer = None
        self.stdout_handler = None
        self.window_moved = False

        self.boom_pivot = NodePath('boom_pivot')
        self.cam_point = NodePath('cam_point')
        self.boom_pivot.reparent_to(render)
        self.cam_point.reparent_to(self.boom_pivot)

        self.value_selector = FiniteRepetitionSelector("*", 2)

        self.client_repository.createDistributedObject(distObj=self.drone, zoneId=2)

        self.xrsdk = None
        self.counter = 0

        self.drone.start()
        self.drone.hide()

    def update_mouse_offsets(self):
        x = base.mouseWatcherNode.get_mouse_x()
        y = base.mouseWatcherNode.get_mouse_y()
        self.current_mouse_pos = (x * base.camLens.get_fov().x * self.mouse_sensitivity,
                                  y * base.camLens.get_fov().y * self.mouse_sensitivity)

        if (-self.current_mouse_pos[0] != 0 or self.current_mouse_pos[1] != 0):
            if (-1 < self.current_mouse_pos[0] < 1 and -1 < self.current_mouse_pos[1] < 1):
                self.offset_diffx = - self.current_mouse_pos[0]
                self.offset_diffy = self.current_mouse_pos[1]
            else:
                self.offset_diffx = 0
                self.offset_diffy = 0
        else:
            self.offset_diffx = 0
            self.offset_diffy = 0

    def set_initial_position(self, pos, target):
        self.initial_position = pos
        self.initial_destination = target
        self.use_hpr = False
        self.reset_to_initial()

    def set_initial_position_hpr(self, pos, hpr):
        self.initial_position = pos
        self.initial_hpr = hpr
        self.use_hpr = True
        self.reset_to_initial()

    def set_scale(self, size):
        self.size = size
        self.drone.setScale(self.size)

    def reset_to_initial(self):
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
        self.xrsdk.Reset()

    def ralt_down(self):
        self.pre_reset_glasses_rotation = list(map(float, self.xrsdk.ReadArSensors().split(",")))
        self.xrsdk.Reset()
        current_glasses_rotation = list(map(float, self.xrsdk.ReadArSensors().split(",")))
        self.current_glasses_rotation = Quat(current_glasses_rotation[3], current_glasses_rotation[0],
                                              current_glasses_rotation[1], current_glasses_rotation[2])


        new_quat = self.unity_to_panda3d_quaternion(
            Quat(current_glasses_rotation[0], current_glasses_rotation[1], current_glasses_rotation[2], current_glasses_rotation[3]))
        flip_rotation = Quat()
        flip_rotation.setFromAxisAngle(180, Vec3(0, 0, 1))
        self.working_current_glasses_rotation = (flip_rotation * Quat(new_quat[3], new_quat[0], new_quat[1], new_quat[2]))

        self.current_rotation = self.drone.get_quat()
        self.current_camera_rotation = base.camera.get_quat()
        #self.current_rotation = self.drone.get_hpr()

        #base.camera.set_quat(self.current_glasses_rotation)
        self.firstpersonlook_activated = True

    def ralt_up(self):
        #base.camera.set_hpr(self.current_rotation)
        #self.drone.set_hpr(self.current_rotation)
        #base.camera.set_quat(self.current_rotation)
        #self.drone.set_quat(self.current_rotation)
        self.firstpersonlook_activated = False

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
        self.current_freelook_rot_r = base.camera.get_r()
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
        # Unbinds the movement controller and restores the previous state
        raise NotImplementedError()

    @property
    def clock_obj(self):
        return base.taskMgr.globalClock

    def setup(self):  # Notice how most of these keybinds are for natural movements
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

        # base.accept("f3", base.toggle_wireframe)

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
        base.accept("lalt", self.alt_down)
        base.accept("lalt-up", self.alt_up)
        base.accept("shift", self.shift_down)
        base.accept("shift-up", self.shift_up)
        base.accept("wheel_down", self.wheel_down)
        base.accept("wheel_up", self.wheel_up)
        base.accept("ralt", self.ralt_down)
        base.accept("ralt-up", self.ralt_up)
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

    def update_first_character_quat(self, initial_quat_first, initial_quat_second, changing_quat_second):
        quat_relative = initial_quat_first - initial_quat_second
        quat = changing_quat_second + quat_relative
        return quat

    def unity_to_panda3d_quaternion(self,unity_quaternion):
        # Flip Y and Z axes
        unity_quaternion = [-unity_quaternion[0], unity_quaternion[2], unity_quaternion[1], -unity_quaternion[3]]

        # Change the sign of the Y and Z components
        panda3d_quaternion = Quat(unity_quaternion[0], -unity_quaternion[1], unity_quaternion[2], unity_quaternion[3])

        return panda3d_quaternion

    def update(self, task):
        delta = self.clock_obj.get_dt()

        # Update mouse first
        if base.mouseWatcherNode.has_mouse():
            x = base.mouseWatcherNode.get_mouse_x()
            y = base.mouseWatcherNode.get_mouse_y()
            self.current_mouse_pos = (x * base.camLens.get_fov().x * self.mouse_sensitivity,
                                      y * base.camLens.get_fov().y * self.mouse_sensitivity)

            if not self.mouse_enabled:
                self.diffx = -self.current_mouse_pos[0] - self.offset_diffx  # TODO: FIX with M_relative in 11.0 (self.last_mouse_pos[0] -
                # self.current_mouse_pos[0])
                self.diffy = self.current_mouse_pos[1] - self.offset_diffy  # (self.last_mouse_pos[1] - self.current_mouse_pos[1])
                # sometimes the hardest bugs to solve at the deepest ends of your own thoughts
                # are you trying to make sense of something that someone else has written when
                # you have absolutely no knowledge of that and made sure not to, with the hope
                # that the most simple of APIs could not be messed up, but they were

                # if self.last_mouse_pos[0] == 0 and self.last_mouse_pos[1] == 0:
                #     diffx = 0
                #     diffy = 0
                #             if self.mmb_activated:
                #                 base.camera.setR(base.camera.getR() + x * rot_speed)
                #                 self.drone.setR(base.camera.getR())
                #             else:
                #                 base.camera.setH(base.camera.getH() + -x * rot_speed)
                #                 self.drone.setH(base.camera.getH() - 180)

                if self.freelook_activated and not self.shift_activated or self.ctrl_activated:
                    self.boom_pivot.set_pos(self.drone.get_pos())
                    if self.mmb_activated:
                        self.boom_pivot.setR(self.boom_pivot.get_r() - self.diffx)
                        # base.camera.set_r(base.camera.get_r() - diffx)
                    else:
                        self.boom_pivot.setH(self.boom_pivot.get_h() + self.diffx)
                        self.boom_pivot.setP(self.boom_pivot.get_p() + self.diffy)
                    # if self.mmb_activated:
                    #     self.boom_pivot.setR(self.drone, -diffx)
                    # else:
                    #     self.boom_pivot.setH(self.drone, diffx)
                    #     self.boom_pivot.setP(self.drone, diffy)
                    self.cam_point.set_pos((0,-self.freelook_distance, 0))

                    # self.boom_arm.update((0,0,0), np.array([-self.freelook_distance, 0, 0]),.1)
                    base.camera.setPos(render.getRelativePoint(self.boom_pivot, self.cam_point.get_pos()))

                    base.camera.look_at(self.drone.get_pos())
                    self.current_freelook_rot_r = self.current_freelook_rot_r - self.diffx
                    if self.mmb_activated:
                        base.camera.set_r(self.current_freelook_rot_r)

                    self.drone.show()

                elif self.firstpersonlook_activated:
                    gyro_values = list(map(float, self.xrsdk.ReadArSensors().split(",")))
                    print(gyro_values)
                    new_quat = self.unity_to_panda3d_quaternion(Quat(gyro_values[0], gyro_values[1], gyro_values[2], gyro_values[3]))
                    flip_rotation = Quat()
                    flip_rotation.setFromAxisAngle(180, Vec3(0, 0, 1))
                    working_gyro_values = (flip_rotation * Quat(new_quat[3], new_quat[0], new_quat[1], new_quat[2]))
                    working_gyro_values.normalize()
                    vertical_tilt_quat = Quat()
                    vertical_tilt_quat.setFromAxisAngle(-22, (1, 0, 0)) # 22° tilt
                    base.camera.set_quat(working_gyro_values * (vertical_tilt_quat * flip_rotation * self.current_camera_rotation))

                else:
                    self.boom_pivot.set_hpr(0,0,0) # hpr = ypr
                    self.drone.hide()

                    base.camera.set_pos(self.drone.get_pos())
                    if self.mmb_activated:
                        self.drone.setR(self.drone, - self.diffx)
                    else:
                        self.drone.setH(self.drone, self.diffx)
                        self.drone.setP(self.drone, self.diffy)
                    base.camera.set_quat(self.drone.get_quat())

                    # Compute movement in render space
                    movement_direction = (Vec3(self.movement[1], self.movement[0], self.movement[2]) * self.speed * delta * 100.0)

                    # transform by the camera direction
                    camera_quaternion = base.camera.get_quat(base.render)
                    translated_direction = camera_quaternion.xform(movement_direction)

                    # # z-force is independent of camera direction
                    # translated_direction.add_z(
                    #      * delta * 120.0 * self.speed)

                    self.velocity += translated_direction  # * 0.15

                    # apply the new position
                    base.camera.set_pos(base.camera.get_pos() + self.velocity)
                    self.drone.setPos(base.camera.getPos())

                    # fade out velocity
                    self.velocity = self.velocity * max(0.0, 1.0 - delta * 60.0 / max(0.001, self.smoothness))

                self.last_mouse_pos = self.current_mouse_pos[:]
                if not self.mouse_enabled:
                    # print("" + str(base.win.getXSize() / 2) + " " + str(base.win.getYSize() / 2))
                    base.win.movePointer(0, int(base.win.getXSize() / 2), int(base.win.getYSize() / 2))
                    # TODO: Fix Quaternion-Based-Bobbing. GPT solutions do not work.
        return task.cont

    def play_motion_path(self, points, point_duration=1.2):
        # Plays a motion path from the given set of points
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

        lerp = (self.clock_obj.get_frame_time() - self.curve_time_start) / \
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

