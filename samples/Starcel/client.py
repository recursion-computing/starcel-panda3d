# Networked actor repos
from ClientRepository import GameClientRepository
from DistributedSmoothActor import DistributedSmoothActor

from direct.showbase.ShowBase import ShowBase  # Loader
from panda3d.core import *
# from panda3d.core import Vec3, load_prc_file_data, KeyboardButton, NodePath, PandaNode, TextNode
import gltf

# import direct.directbase.DirectStart
# from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from inputfield import InputField

import os, sys, math, socket, subprocess, cmdix, xarray as xr, numpy as np, fast_autocomplete, dill
from random import random, randint, seed
# from p10ga_py import *
from skimage.measure import marching_cubes
import scipy.sparse.linalg
import scipy
import time, uuid, copy, asyncio
from threading import Thread, Timer
import limeade

# Change to the current directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))


class StdoutHandler:
    def __init__(self):
        self.last_output = ""

    def start(self):
        self._handled_stdout = sys.stdout
        sys.stdout = self

    def write(self, data: str):
        # write(data="") is called for the end kwarg in print(..., end="")
        if data:
            # print("does this work?")
            self.last_output += data
            self._handled_stdout.write(data)

    def end(self):
        sys.stdout = self._handled_stdout

    def flush(self):
        self._handled_stdout.flush()


class Avatar:
    def __init__(self, client_repository):
        self.client_repository = client_repository
        self.mmb_activated = False
        self.alt_activated = False
        self.ctrl_activated = False
        self.freelook_activated = False
        self.freelook_distance = 16
        self.drone = DistributedSmoothActor(self.client_repository)
        self.boom_arm = Cylinder(np.array(self.drone.getPos()),np.array(self.drone.getPos()) + np.array([0,self.freelook_distance,0]),1,self.drone)
        self.value_selector = FiniteRepetitionSelector("*", 2)

        self.client_repository.createDistributedObject(distObj=self.drone, zoneId=2)

        # self.floater = NodePath(PandaNode("floater"))
        # self.floater.reparentTo(self.drone)
        # self.floater.setZ(2.0)

        # mouseWatcherNode actually also handles keyboard
        self.isDown = base.mouseWatcherNode.is_button_down

        taskMgr.add(self.move, "moveTask")

        base.accept("mouse2", self.mmb_down)
        base.accept("mouse2-up", self.mmb_up)
        base.accept("alt", self.alt_down)
        base.accept("alt-up", self.alt_up)
        base.accept("ctrl", self.ctrl_down)
        base.accept("ctrl-up", self.ctrl_up)
        base.accept("alt-wheel_up", self.alt_wheel_up)
        base.accept("alt-wheel_down", self.alt_wheel_down)

        self.drone.start()

    def alt_wheel_up(self):
        if self.freelook_activated:
            print(self.freelook_distance)
            self.freelook_distance = self.value_selector.decrease_value(self.freelook_distance)

    def alt_wheel_down(self):
        if self.freelook_activated:
            print(self.freelook_distance)
            self.freelook_distance = self.value_selector.increase_value(self.freelook_distance)

    def wheel_up(self):
        pass

    def wheel_down(self):
        pass

    def ctrl_down(self):
        self.ctrl_activated = True

    def ctrl_up(self):
        self.ctrl_activated = False

    def alt_down(self):
        self.alt_activated = True

    def alt_up(self):
        self.alt_activated = False

    def mmb_down(self):
        self.mmb_activated = True

    def mmb_up(self):
        self.mmb_activated = False

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        # Get the time that elapsed since last frame.  We multiply this with
        # the desired speed in order to find out with which distance to move
        # in order to achieve that desired speed.
        dt = globalClock.getDt()

        # If a move-key is pressed, move drone in the specified direction.
        if self.isDown(KeyboardButton.asciiKey(b"w")):
            self.drone.setY(self.drone, -10 * dt)
        if self.isDown(KeyboardButton.asciiKey(b"a")):
            self.drone.setX(self.drone, 10 * dt)
        if self.isDown(KeyboardButton.asciiKey(b"s")):
            self.drone.setY(self.drone, 10 * dt)
        if self.isDown(KeyboardButton.asciiKey(b"d")):
            self.drone.setX(self.drone, -10 * dt)
        if self.isDown(KeyboardButton.asciiKey(b"e")):
            self.drone.setZ(self.drone, 10 * dt)
        if self.isDown(KeyboardButton.asciiKey(b"q")):
            self.drone.setZ(self.drone, -10 * dt)
        # if self.isDown(KeyboardButton.ascii_key("alt")):
        #     print("alt clicked")


        # update distributed position and rotation
        # self.drone.setDistPos(self.drone.getX(), self.drone.getY(), self.drone.getZ())
        # self.drone.setDistHpr(self.drone.getH(), self.drone.getP(), self.drone.getR())

        # If drone is moving, loop the run animation.
        # If he is standing still, stop the animation.
        # currentAnim = self.drone.getCurrentAnim()
        #
        # if self.isDown(KeyboardButton.asciiKey(b"w")):
        #     pass
        #     #if currentAnim != "run":
        #         #self.drone.loop("run")
        # elif self.isDown(KeyboardButton.asciiKey(b"s")):
        #     # Play the walk animation backwards.
        #     #if currentAnim != "walk":
        #         #self.drone.loop("walk")
        #     self.drone.setPlayRate(-1.0, "walk")
        # elif self.isDown(KeyboardButton.asciiKey(b"a")) or self.isDown(KeyboardButton.asciiKey(b"d")):
        #     #if currentAnim != "walk":
        #         #self.drone.loop("walk")
        #     self.drone.setPlayRate(1.0, "walk")
        # else:
        #     if currentAnim is not None:
        #         #self.drone.stop()
        #         #self.drone.pose("walk", 5)
        #         self.isMoving = False

        # If the camera is too far from drone, move it closer.
        # If the camera is too close to drone, move it farther.

        # camvec = self.drone.getPos() - base.camera.getPos()
        # camvec.setZ(0)
        # camdist = camvec.length()
        # camvec.normalize()
        # if camdist > 10.0:
        #     base.camera.setPos(base.camera.getPos() + camvec * (camdist - 10))
        #     camdist = 10.0
        # if camdist < 5.0:
        #     base.camera.setPos(base.camera.getPos() - camvec * (5 - camdist))
        #     camdist = 5.0

        # The camera should look in drone's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above drone's head.
        # base.camera.lookAt(self.floater)

        rot_speed = 100

        if self.alt_activated:
            self.freelook_activated = True
        else:
            self.freelook_activated = False

        if self.freelook_activated:
            self.boom_arm.update(self.drone.getPos(), np.array(self.drone.getPos()) + np.array([0,self.freelook_distance,0]), 1)
            #swap to freelook camera
            base.camera.setPos(self.boom_arm.line_end[0], self.boom_arm.line_end[1], self.boom_arm.line_end[2])

            new_rot = self.boom_arm.look_at_rotation(np.array(self.boom_arm.line_end), np.array(self.drone.getPos()))
            # print(new_rot)
            # print(self.boom_arm.line_end)
            # print(self.drone.getPos())
            # print("\n")
            # base.camera.setR(base.camera.getR() + 180)
            if new_rot is not None and not np.isnan(new_rot).any():
                base.camera.setHpr(new_rot[0] + 180, new_rot[1], new_rot[2])

        else:
            base.camera.setPos(self.drone.getPos())
            if base.mouseWatcherNode.hasMouse():
                x = base.mouseWatcherNode.getMouseX()
                y = base.mouseWatcherNode.getMouseY()
                base.camera.setP(base.camera.getP() + y * rot_speed)
                self.drone.setP(base.camera.getP() + 90)
                if self.mmb_activated:
                    base.camera.setR(base.camera.getR() + x * rot_speed)
                    self.drone.setR(base.camera.getR())
                else:
                    base.camera.setH(base.camera.getH() + -x * rot_speed)
                    self.drone.setH(base.camera.getH() - 180)



        return task.cont



class FiniteRepetitionSelector():
    # +1
    # 1     2     3     4     5     6
    # +2
    # 0     2     4     6     8     10     12
    #
    # *2
    # 2 + 2     4 + 4     8 + 8     16 + 16    32 + 32
    #
    # ^ 2
    # 2 * 2     4 * 4     16 * 16     256 * 256
    #
    # ↑2
    # 2 ^ 2 = 4     4 ^ 4     256 ^ 256
    #
    # ↑↑2
    # 2↑2 = 4     4↑4 = 4 ^ 4 ^ 4 ^ 4
    #
    # 2↑↑2 = 2↑2 = 4
    #
    # 2↑↑↑↑2 = 2↑↑↑2 = 2↑↑2
    #
    # auto(negate/direction)?
    # auto(negate/direction) threshold: 1

    def __init__(self, current_operator = "+", current_operand = 2):
        self.operators = ["C/S", "+", "*", "^", "↑", "↑↑"]
        self.current_operator = current_operator
        self.current_operand = current_operand
        self.autonegate_threshold = 0.0
        self.autonegate = False

    def autonegate_value(self, value):
        if self.autonegate:
            if self.autonegate_threshold > value > -1 * self.autonegate_threshold:
                return -1 * value
        return value

    def basic_tetration(self, a, b):
        # a is the first input value and b is the second input value
        total = a
        for i in range(1, round(b)):
            total = a ^ total
        return total

    def decrease_value(self, value):
        value = self.autonegate_value(value)
        if self.current_operator == self.operators[1]:
            return value - self.current_operand
        if self.current_operator == self.operators[2]:
            return value / self.current_operand
        if self.current_operator == self.operators[3]:
            return pow(value, (1 / self.current_operand))
        if self.current_operator == self.operators[4]:
            return self.basic_tetration(value,self.current_operand)
        return value

    def increase_value(self, value):
        value = self.autonegate_value(value)
        if self.current_operator == self.operators[1]:
            return value + self.current_operand
        if self.current_operator == self.operators[2]:
            return value * self.current_operand
        if self.current_operator == self.operators[3]:
            return pow(value, self.current_operand)
        return value

class SpatialDimensionSelector():
    def __init__(self):
        Line2 = [[-1.000000, 0.000000, 0.000000], [1.000000, 0.000000, 0.000000]]
        Plane4 = [[0.000000, 1.000000, 0.000000], [1.000000, 0.000000, 0.000000], [0.000000, -1.000000, 0.000000],
                  [-1.000000, 0.000000, 0.000000]]
        Optimal6 = [[1.000000, 0.000000, 0.000000], [-1.000000, 0.000000, 0.000000], [0.000000, 1.000000, 0.000000],
                    [0.000000, -1.000000, 0.000000], [0.000000, 0.000000, 1.000000], [0.000000, 0.000000, -1.000000]]
        Optimal4 = [[0.577350, 0.577350, 0.577350], [-0.577350, -0.577350, 0.577350], [-0.577350, 0.577350, -0.577350],
                    [0.577350, -0.577350, -0.577350]]
        Wolfram5 = [[-1.000000, 0.000000, 0.000000], [1.000000, 0.000000, 0.000000], [0.000000, -0.866025, -0.500000],
                    [0.000000, 0.866025, -0.500000], [0.000000, 0.000000, 1.000000]]
        Optimal6_0 = [[1.000000, 0.000000, 0.000000], [-1.000000, 0.000000, 0.000000], [0.000000, 1.000000, 0.000000],
                      [0.000000, -1.000000, 0.000000], [0.000000, 0.000000, 1.000000], [0.000000, 0.000000, -1.000000]]
        Wolfram7 = [[0.000000, 0.000000, -1.000000], [0.000000, 0.000000, 1.000000], [1.000000, 0.000000, 0.000000],
                    [0.309017, -0.951057, 0.000000], [0.309017, 0.951057, 0.000000], [-0.809017, -0.587785, 0.000000],
                    [-0.809017, 0.587785, 0.000000]]
        Optimal8 = [[0.859533, 0.000000, 0.511081], [-0.859533, 0.000000, 0.511081], [0.000000, 0.859533, 0.511081],
                    [0.000000, -0.859533, 0.511081], [0.607781, 0.607781, -0.511081], [0.607781, -0.607781, -0.511081],
                    [-0.607781, 0.607781, -0.511081], [-0.607781, -0.607781, -0.511081]]
        Cube8 = [[0.577350, 0.577350, 0.577350], [-0.577350, 0.577350, 0.577350], [0.577350, -0.577350, 0.577350],
                 [-0.577350, -0.577350, 0.577350], [0.577350, 0.577350, -0.577350], [-0.577350, 0.577350, -0.577350],
                 [0.577350, -0.577350, -0.577350], [-0.577350, -0.577350, -0.577350]]
        Wolfram9 = [[-0.37796447300922725, -0.6546536707079771, -0.6546536707079771],
                    [-0.37796447300922725, -0.6546536707079771, 0.6546536707079771],
                    [-0.37796447300922725, 0.6546536707079771, -0.6546536707079771],
                    [-0.37796447300922725, 0.6546536707079771, 0.6546536707079771],
                    [0.7559289460184545, 0., -0.6546536707079771], [0.7559289460184545, 0., 0.6546536707079771],
                    [-1., 0., 0.], [0.5, -0.8660254037844386, 0.], [0.5, 0.8660254037844386, 0.]]
        Wolfram10 = [[-0.8944271909999157, 0., -0.44721359549995787], [0.8944271909999157, 0., 0.44721359549995787],
                     [-0.7236067977499789, -0.5257311121191336, 0.44721359549995787],
                     [-0.7236067977499789, 0.5257311121191336, 0.44721359549995787],
                     [-0.276393202250021, -0.85065080835204, -0.44721359549995787],
                     [-0.276393202250021, 0.85065080835204, -0.44721359549995787],
                     [0.276393202250021, -0.85065080835204, 0.44721359549995787],
                     [0.276393202250021, 0.85065080835204, 0.44721359549995787],
                     [0.7236067977499789, -0.5257311121191336, -0.44721359549995787],
                     [0.7236067977499789, 0.5257311121191336, -0.44721359549995787]]
        Wolfram11 = [[0., 0., 1.], [-0.8944271909999157, 0., -0.44721359549995787],
                     [0.8944271909999157, 0., 0.44721359549995787],
                     [-0.276393202250021, -0.85065080835204, -0.44721359549995787],
                     [-0.276393202250021, 0.85065080835204, -0.44721359549995787],
                     [0.276393202250021, -0.85065080835204, 0.44721359549995787],
                     [0.276393202250021, 0.85065080835204, 0.44721359549995787],
                     [-0.7236067977499789, -0.5257311121191336, 0.44721359549995787],
                     [-0.7236067977499789, 0.5257311121191336, 0.44721359549995787],
                     [0.7236067977499789, -0.5257311121191336, -0.44721359549995787],
                     [0.7236067977499789, 0.5257311121191336, -0.44721359549995787]]
        Optimal12 = [[0.850651, 0.000000, -0.525731], [0.525731, -0.850651, 0.000000], [0.000000, -0.525731, 0.850651],
                     [0.850651, 0.000000, 0.525731], [-0.525731, -0.850651, 0.000000], [0.000000, 0.525731, -0.850651],
                     [-0.850651, 0.000000, -0.525731], [-0.525731, 0.850651, 0.000000], [0.000000, 0.525731, 0.850651],
                     [-0.850651, 0.000000, 0.525731], [0.525731, 0.850651, 0.000000], [0.000000, -0.525731, -0.850651]]


class Cylinder():
    def __init__(self, line_start, line_end, line_thickness, reparent_to):
        self.line_start = np.array(line_start)
        self.line_end = np.array(line_end)
        self.line_thickness = line_thickness
        self.line_midpoint = (np.array(line_start) + np.array(line_end)) / 2.0
        self.model = loader.loadModel("models/Cylinder.bam")
        self.model.reparent_to(reparent_to)
        euler_angles = self.look_at_rotation(self.line_midpoint, self.line_end)
        print("aaaaaaaaaa")
        print(euler_angles)
        euler_angles = [x + 360 if x < 0 else x for x in euler_angles]
        print(euler_angles)
        self.model.setPosHprScale(self.line_midpoint[0], self.line_midpoint[1], self.line_midpoint[2], euler_angles[0], euler_angles[1], euler_angles[2], line_thickness, line_thickness, float(np.sqrt((self.line_end - self.line_start).dot((self.line_end - self.line_start)))))

    def update(self, line_start, line_end, line_thickness):
        self.line_start = np.array(line_start)
        self.line_end = np.array(line_end)
        self.line_thickness = line_thickness
        self.line_midpoint = (np.array(line_start) + np.array(line_end)) / 2.0
        euler_angles = self.look_at_rotation(self.line_midpoint, self.line_end)
        self.model.setPosHprScale(self.line_midpoint[0], self.line_midpoint[1], self.line_midpoint[2], euler_angles[0], euler_angles[1], euler_angles[2], line_thickness, line_thickness, float(np.sqrt((self.line_end - self.line_start).dot((self.line_end - self.line_start)))))

    def look_at_rotation(self, start, target):
        # Check if both start and target vectors are zero
        start_is_zero = np.allclose(start, [0.0, 0.0, 0.0])
        target_is_zero = np.allclose(target, [0.0, 0.0, 0.0])

        # Add an offset to both start and target vectors if they are zero
        if start_is_zero and target_is_zero:
            start += np.array([1.0, 1.0, 1.0])
            target += np.array([1.0, 1.0, 1.0])

        # Calculate the forward direction and up direction
        forward = (target - start)
        forward_norm = np.linalg.norm(forward)

        # Check if the norm is zero
        if forward_norm == 0:
            # Handle the case when the vectors are parallel (no rotation needed)
            return (0.0, 0.0, 0.0)

        forward /= forward_norm
        up = np.array([0.0, 1.0, 0.0])  # Assuming the up direction is the positive Y-axis

        # Calculate the right direction using cross product
        right = np.cross(up, forward)
        right_norm = np.linalg.norm(right)

        # Check if the norm is zero
        if right_norm == 0:
            # Handle the case when the vectors are parallel (no rotation needed)
            return (0.0, 0.0, 0.0)

        right /= right_norm

        # Calculate the up direction using cross product again
        new_up = np.cross(forward, right)

        # Build the rotation matrix
        rotation_matrix = np.column_stack((right, new_up, -forward))

        # Convert the rotation matrix to Euler angles
        euler_angles = (np.degrees(np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])),
        np.degrees(
            np.arctan2(-rotation_matrix[2, 0], np.sqrt(rotation_matrix[2, 1] ** 2 + rotation_matrix[2, 2] ** 2))),
        np.degrees(np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])))
        return tuple(euler_angles)



class MainApp(ShowBase):
    # Setup window size, title and so on
    load_prc_file_data("", """
    win-size 1920 1056
    window-title Starcel
    """)

    def __init__(self):
        def set_relative_mode_and_hide_cursor():
            props = WindowProperties()
            props.setCursorHidden(True)
            # TODO: Update to M_Relative in Panda 11.0
            props.setMouseMode(WindowProperties.M_confined)
            base.win.requestProperties(props)

        def normal_mouse_mode():
            props = WindowProperties()
            props.setCursorHidden(False)
            props.setMouseMode(WindowProperties.M_absolute)
            base.win.requestProperties(props)

        def getalias():
            # load aliases from csv into xarray
            aliasfunctions = xr.DataArray(
                np.loadtxt("C:/Users/xnick/Documents/Unreal Projects/starcel/Content/SCfiles/data/aliasfunctions.csv",
                           delimiter=",", dtype=str))
            available_functions = aliasfunctions.isel(dim_1=0)[1:]
            # print([func.split('/') for func in available_functions])
            for function in np.array(available_functions):
                print("'" + function + "'" + ",")
            flat_list = [item for sublist in [func.split('/') for func in np.array(available_functions)] for item in sublist]
            return flat_list  # available_functions

        # Collect all aliases
        # test_keys = np.array(getalias()).tolist()
        # print(test_keys)
        words = {}
        for key in getalias():
            words[key] = {}

        # stdout handler so it cant be sent over tcp
        self.stdout_handler = StdoutHandler()
        self.stdout_handler.start()

        # Render Pipeline setup
        pipeline_path = "../../"

        sys.path.insert(0, pipeline_path)

        from rpcore import RenderPipeline, SpotLight
        # from rpcore.util.movement_controller import MovementController

        self.render_pipeline = RenderPipeline()
        self.render_pipeline.create(self)
        # self.render.set_shader_auto()
        # gltf.patch_loader(self.loader)

        # Set time of day
        self.render_pipeline.daytime_mgr.time = 0

        # Init movement controller
        # self.controller = MovementController(self)
        #self.controller.setup()
        set_relative_mode_and_hide_cursor()

        # Fonts and theme
        fontPath = "SourceCodePro-Regular.ttf"
        font = loader.loadFont(fontPath, color=(1, 1, 1, 1), renderMode=TextFont.RMSolid)
        font2 = loader.loadFont(fontPath, color=(1, 1, 1, 1))



        # HUD setup
        self.hud_bound_textNode = None
        # callback function to set text
        # def setText(textEntered):
        #     textObject.setText(textEntered)

        # #clear the text
        # def clearText():
        #     entry.enterText('')

        # #add text entry
        # entry = DirectEntry(text = "", pos=(-1.6,0.0,.9), scale=.05, entryFont=font2, command=setText, initialText="=", numLines = 2, width=800, focus=0, focusInCommand=clearText, suppressKeys=0, frameColor=(0, 0, 0, 0))

        # It is necessary to set up the white color text property for selected text
        props_mgr = TextPropertiesManager.get_global_ptr()
        col_prop = TextProperties()
        col_prop.set_text_color((1., 1., 1., 1.))
        props_mgr.set_properties("white", col_prop)

        # Define the transformation of the InputField
        pos = Vec3(-1.7, 0., .9)
        scale = .05
        width = 68

        geoms = NodePath("input_field_geoms")

        cm = CardMaker("inputfield_geom_normal")
        cm.set_frame(0., width, -.5, 1.)
        cm.set_color(.5, .5, .5, 1.)
        cm.set_has_uvs(False)
        cm.set_has_normals(False)
        geoms.attach_new_node(cm.generate())

        cm = CardMaker("inputfield_geom_hilited")
        cm.set_frame(0., width, -.5, 1.)
        cm.set_color(.5, .5, .5, 1.)
        cm.set_has_uvs(False)
        cm.set_has_normals(False)
        geoms.attach_new_node(cm.generate())

        def fix_pyout3dtext(pynode, text):
            pynode.node().setText(text)

        def submit_scell(text):
            print("ran submit scell")
            output = None

            # Forced to put this here to comply with local scope. Perhaps this should be replaced with globals or restructured into its own file
            def scenegraph(_):
                lsb = LineStream()
                render.ls(lsb)
                text = ''
                while lsb.isTextAvailable():
                    text += lsb.getLine() + '\n'
                return text

            self.stdout_handler.last_output = ""
            input_text = text
            print(text)
            parsed = input_text.strip().split(' ')
            print(locals().keys())
            if parsed[0] in list(cmdix.listcommands()):  # linux commands
                output = cmdix.runcommandline(input_text)
            elif ((parsed[0]) in locals().keys()):  # functions defined in this file
                print("customfunc called")
                output = locals()[parsed[0]](parsed[1:])  # TODO: Support for no argument functions
            else:
                # print("eval called")
                try:
                    output = exec(
                        input_text)  # Executing of receieved statement. Exec relies on the stdout print statements to receive output whereas when this is switched to eval, output is sent back over the socket
                    # output = repr(self.stdout_handler.last_output)
                    # print(self.stdout_handler.last_output)
                except Exception as e:
                    output = e

            try:
                if not str(output) or output is None or output == "":
                    # print("FFFF" + stdout_handler.last_output)
                    output = repr(self.stdout_handler.last_output)
                    # t.start()
                    # if output is None or output == "":
                    # output = self.tempoutput
            except:
                pass

            try:
                print(self.hud_bound_textNode.node())
                # self.hud_bound_textNode.node().setText(output)
                pyout = spawn_scell(output, self.hud_bound_textNode.getPos() + (0, 0, -2))
                t = Timer(.02, fix_pyout3dtext, (pyout, output,))
                t.start()
                # thread = Thread(target = spawn_scell, args = (output, self.hud_bound_textNode.getPos() + (0,0,-2),), daemon=True)
                # thread.start()
                # thread.join()
                print(self.hud_bound_textNode.node())
                # fix_pyout3dtext(pyout, output)
            except:
                pass
            # self.pyout.node().setText(output)
            # time.sleep(2)

        # base.accept("shift-enter", submit_scell)

        # Define a function that will be called when committing the entry text
        def on_commit_func(text, field_name):
            print(f"The following has been entered into {field_name}:", text)
            submit_scell(text)

        def on_keystroke(text):
            if self.hud_bound_textNode is not None:
                try:
                    # render.ls()
                    # print(self.hud_bound_textNode)
                    self.hud_bound_textNode.node().setText(entry._edited_text)
                    self.hud_bound_textNode.node().forceUpdate()
                    self.hud_bound_textNode.getChild(0).node().clearSolids()
                    # print(self.hud_bound_textNode.getChild(0).node())
                    self.hud_bound_textNode.getChild(0).node().addSolid(
                        CollisionBox(self.hud_bound_textNode.getTightBounds()[0] - self.hud_bound_textNode.getPos(),
                                     self.hud_bound_textNode.getTightBounds()[1] - self.hud_bound_textNode.getPos()))
                except:
                    pass
                # print("HUD:", entry._edited_text)

        # Create two input fields
        self.buttonThrowers[0].node().set_keystroke_event("keystroke_event")
        self.accept("keystroke_event", on_keystroke)

        on_commit = (on_commit_func, ["inputfield_1"])
        entry = InputField(self, pos, scale, width, geoms, on_commit)

        # pos = Vec3(-.5, 0., .5)
        # on_commit = (on_commit_func, ["inputfield_2"])
        # self.field2 = InputField(self, pos, scale, width, geoms, on_commit)

        # class MyVersionOfDirectEntry(DirectEntry):
        #     def _handleTyping( self, *args, **kwargs ):
        #         # do your "decoration" here.
        #         super( MyVersionOfDirectEntry, self )._handleTyping( *args, **kwargs )
        #         print("hi")
        #         #print(hud_bound_textNode)
        #         #hud_bound_textNode.getChild(0).node().setText(textEntered)

        # def _handleTyping2(self, guiEvent):
        #     print(hud_bound_textNode)
        #     hud_bound_textNode.getChild(0).node().setText(textEntered)
        #     self._autoCapitalize()

        # entry._handleTyping = _handleTyping2

        # Scene Setup
        # Load test scene
        model = loader.loadModel("scene/TestScene.bam")
        model.reparent_to(render)
        model.setPos(0, 0, -10)
        model.node().setIntoCollideMask(BitMask32.bit(1))
        Cylinder([1, 1, 1], [100, 100, 100], 10, render)

        # model = loader.loadModel("/c/Users/xnick/Downloads/panda3d-master/panda3d-master/models/panda.egg")
        # model.reparent_to(render)

        self.ambientLight = self.render.attachNewNode(AmbientLight('ambient'))
        self.ambientLight.node().setColor((0.1, 0.1, 0.1, 1))
        self.render.setLight(self.ambientLight)

        # collisiondebugger = CollisionVisualizer("debug")
        # collisiondebugger.reparent_to(render)
        # render.attachNewNode(collisiondebugger)
        # self.render_pipeline.prepare_scene(model)

        # text = TextNode('text')
        # text.setText("Hello, World!")
        # text.setFont(font)
        # text.setAlign(TextNode.ACenter)
        # textNode = render.attachNewNode(text.generate())
        # textNode.getChild(0).node().setIntoCollideMask(BitMask32.bit(1))
        # # textNode.setScale(50)
        # textNode.setScale(50,10,50)
        # textNode.node().setIntoCollideMask(BitMask32.bit(1))

        # fromObject = textNode.attachNewNode(CollisionNode('TextColNode'))
        # #fromObject.show()
        # print(textNode.getTightBounds())
        # fromObject.node().addSolid(CollisionBox(textNode.getTightBounds()[0]/50, textNode.getTightBounds()[1]/50))
        # textNode.setH(textNode, 30)
        # textNode.setP(textNode, 30)

        # Setup Collision
        # CollisionTraverser and a Collision Handler is set up
        self.picker = CollisionTraverser()
        self.picker.showCollisions(render)
        self.pq = CollisionHandlerQueue()

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))  # BitMask32.bit(1))
        # self.box.setCollideMask(BitMask32.bit(1))

        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)

        def mouseTask():
            print('mouse click')
            #limeade.refresh()
            # check if we have access to the mouse
            if base.mouseWatcherNode.hasMouse():

                # get the mouse position
                mpos = base.mouseWatcherNode.getMouse()

                # set the position of the ray based on the mouse position
                self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
                self.picker.traverse(render)
                # if we have hit something sort the hits so that the closest is first and highlight the node
                if self.pq.getNumEntries() > 0:
                    self.pq.sortEntries()
                    try:
                        pickedObj = self.pq.getEntry(0).getIntoNodePath()
                        print(pickedObj)
                        if pickedObj.getName() == "TextColNode":
                            self.hud_bound_textNode = pickedObj.getParent()
                            entry._d_entry.guiItem.set_focus(True)

                            # print("B" + self.hud_bound_textNode.node().text)
                            entry._d_entry.set(self.hud_bound_textNode.node().text)
                            # print(self.pq.getEntry(0))

                        else:
                            self.win.getProperties().getForeground()
                            entry._d_entry.guiItem.set_focus(False)
                            # entry['focus'] = False
                            hud_bound_textNode = None
                    except:
                        pass
                else:
                    # print("G")
                    # self.controller.setup()
                    self.win.getProperties().getForeground()
                    entry._d_entry.guiItem.set_focus(False)
                    # entry['focus'] = False
                    self.hud_bound_textNode = None

        # self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')
        self.accept("mouse1", mouseTask)

        def spawn_scell_at_player():
            # print(self.controller.showbase.cam.get_pos(self.controller.showbase.render))
            #return spawn_scell(pos=self.controller.showbase.cam.get_pos(self.controller.showbase.render))
            return spawn_scell(pos=Avatar().drone.getPos())

        def spawn_scell(input_text="=", pos=(0, 0, 0)):
            print("equal clicked")
            text = TextNode('Text' + str(uuid.uuid4()))
            text.setText(input_text)
            text.setFont(font)
            text.setAlign(TextNode.ALeft)
            textNode = render.attachNewNode(text)  # text.generate()
            # textNode.getChild(0).node().setIntoCollideMask(BitMask32.bit(1))
            # textNode.setScale(50)
            textNode.setPos(pos)
            textNode.setScale(1, .1, 1)
            textNode.node().setIntoCollideMask(BitMask32.bit(1))

            fromObject = textNode.attachNewNode(CollisionNode('TextColNode'))
            # fromObject.show()
            # print(textNode.getTightBounds())
            fromObject.node().addSolid(CollisionBox(textNode.getTightBounds()[0] - textNode.getPos(),
                                                    textNode.getTightBounds()[1] - textNode.getPos()))
            try:
                entry._d_entry.set(textNode.node().text)
            except:
                pass
            # print(len(entry._edited_text))
            entry._d_entry.guiItem.set_focus(True)
            entry._d_entry.setCursorPosition(len(entry._edited_text))
            self.hud_bound_textNode = textNode
            # print(textNode)
            return textNode

        base.accept("=", spawn_scell_at_player)

        def esc():
            # entry['focus'] = False
            entry._d_entry.guiItem.set_focus(False)
            self.hud_bound_textNode = None
            pass

        base.accept("esc", esc)
        base.accept("m", normal_mouse_mode)

        # initialize the client
        client = GameClientRepository()

        # # Function to put instructions on the screen.
        # def addInstructions(pos, msg):
        #     return OnscreenText(text=msg, style=1, fg=(0, 0, 0, 1), shadow=(1, 1, 1, 1),
        #                         parent=base.a2dTopLeft, align=TextNode.ALeft,
        #                         pos=(0.08, -pos - 0.04), scale=.06)

        # Function to put title on the screen.
        def addTitle(text):
            return OnscreenText(text=text, style=1, pos=(-0.1, 0.09), scale=.08,
                                parent=base.a2dBottomRight, align=TextNode.ARight,
                                fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))

        title = addTitle("Starcel (NOT CONNECTED)")

        # inst1 = addInstructions(0.06, "W|A|S|D: Move avatar)")
        # inst2 = addInstructions(0.12, "esc: Close the client")
        # inst3 = addInstructions(0.24, "See console output")

        def clientJoined():
            title["text"] = "Starcel (CONNECTED)"
            Avatar(client)

        base.accept("client-joined", clientJoined)

    ### Begin Command Processing ###
    # list(cmdix.listcommands()): arch, base64, basename, bunzip2, bzip2, cal, cat, cp, crond, diff, dirname, env, expand, gunzip, gzip, httpd, init, kill, ln, logger, ls, md5sum, mkdir, mktemp, more, mv, nl, pwd, rm, rmdir, sendmail, seq, sh, sha1sum, sha224sum, sha256sum, sha384sum, sha512sum, shred, shuf, sleep, sort, tail, tar, touch, uname, uuidgen, wc, wget, yes, zip

    # cmd = ['echo', 'I like potatos']
    # proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # o, e = proc.communicate()

    # print('Output: ' + o.decode('ascii'))
    # print('Error: '  + e.decode('ascii'))
    # print('code: ' + str(proc.returncode))
    # Linux Commands
    def ls(args):
        windows_command = "dir /b /ogn"
        if not args or args is None:
            # cmdix.runcommandline(windows_command + " ".join(args))
            print(subprocess.check_output(windows_command.split(" "), shell=True, cwd=os.getcwd(), text=True))
            # return subprocess.run(windows_command.split(" "), capture_output=True, text=True, shell=True,cwd=os.path.dirname(os.path.realpath(__file__))).stdout
            # return subprocess.Popen(windows_command.split(" "), stdout=subprocess.PIPE, shell=True, cwd=os.path.dirname(os.path.realpath(__file__))).communicate()[0].decode('utf-8')
            # subprocess.check_output(windows_command.split(" "))
            # subprocess.run(windows_command.split(" "), capture_output=True, shell=True,cwd=os.getcwd()).stdout.decode('utf-8')
            # op = subprocess.Popen(windows_command.split(" "), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            # if op:
            #     o, e = op.communicate()
            #     # print(op.stdout.read())
            #     #print('Error: '  + e.decode('ascii'))
            #     #print('code: ' + str(proc.returncode))
            #     return o.decode('ascii')
        else:
            print(subprocess.check_output(windows_command.split(" ").append(args), shell=True, cwd=os.getcwd(), text=True))
            # return subprocess.run(windows_command.split(" ").append(args), capture_output=True, text=True).stdout
            # return subprocess.Popen(windows_command.split(" ").append(args), stdout=subprocess.PIPE, shell=True, cwd = os.path.dirname(os.path.realpath(__file__))).communicate()[0].decode('utf-8')
            # subprocess.check_output(windows_command.split(" ").append(args))
            # subprocess.run(windows_command.split(" ").append(args), shell=True)
            # op = subprocess.Popen(windows_command.split(" ").append(args), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            # if op:
            #     o, e = op.communicate()
            #     #print('Error: '  + e.decode('ascii'))
            #     #print('code: ' + str(proc.returncode))
            #     return o.decode('ascii')

    def man(args):
        print((subprocess.run(["help"], shell=True, capture_output=True, text=True).stdout))

    # Built-in commands
    def scenegraph(_):
        lsb = LineStream()
        render.ls(lsb)
        text = ''
        while lsb.isTextAvailable():
            text += lsb.getLine() + '\n'
        return text

    def autocomplete(search_word):
        autocomplete = fast_autocomplete.AutoComplete(words=words)
        ac_output = []
        if search_word:
            ac_output = autocomplete.search(word=search_word[0])
        # print(ac_output)
        # return [''.join(x) for x in ac_output]
        return ['_autocomplete'] + ac_output

    def plot(_):
        x, y, z = np.pi * np.mgrid[-1:1:7j, -1:1:7j, -1:1:7j]
        vol = np.cos(x) + np.cos(y) + np.cos(z)
        iso_val = 0.0
        verts, faces, normals, values = marching_cubes(vol, iso_val, spacing=(0.4, 0.4, 0.4))
        return ("_vertices", [["X=%.3f" % x[0] + " Y=%.3f" % x[1] + " Z=%.3f" % x[2]] for x in verts], "_faces",
                [["X=%s" % x[0] + " Y=%s" % x[1] + " Z=%s" % x[2]] for x in faces], "_normals",
                [["X=%.3f" % x[0] + " Y=%.3f" % x[1] + " Z=%.3f" % x[2]] for x in normals])


MainApp().run()