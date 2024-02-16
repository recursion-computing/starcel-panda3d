# Networked actor repos
from ClientRepository import GameClientRepository

from direct.showbase.ShowBase import ShowBase  # Loader
from panda3d.core import *
# from panda3d.core import Vec3, load_prc_file_data, KeyboardButton, NodePath, PandaNode, TextNode
#import gltf

# import direct.directbase.DirectStart
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
import copy
import limeade
from drone_controller import DroneController
from starcelfuncs import FiniteRepetitionSelector, look_at_rotation, SCell

import clr
from pprint import pprint
#clr.AddReference('C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLIBroadcaster\\TCLRayneoAir2CLIBroadcaster.sln')
#clr.AddReference('C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLIBroadcaster\\TCLRayneoAir2CLIBroadcaster')
#clr.AddReference('C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLIBroadcaster\\XRSDK.dll')
#clr.AddReference("C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLIBroadcaster\\bin\Debug\\net6.0\\TCLRayneoAir2CLIBroadcaster.dll")
#clr.AddReference("C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLIBroadcaster\\bin\Debug\\net6.0\\)
#clr.AddReference('C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLIBroadcaster\\XRSDK.dll')

sys.path.append("C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLI\\bin\\Debug\\net7.0\\")
clr.AddReference("TCLRayneoAir2CLI")

#print(clr._available_namespaces)
from FfalconXR import XRSDK  # syntax highlighter may not highlight errors
#print(clr._available_namespaces)

myXRSDK = XRSDK()
#print(dir(XRSDK))
myXRSDK.XRSDK_Init()

# Change to the current directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

global drone
#from ctypes import POINTER, Structure, c_byte, c_uint32, c_float, cast, sizeof

# print(cast(XRSDK.ReadArSensors(), POINTER(c_byte * 5192)).contents)


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


# Convert System.IntPtr to ctypes pointer


# class Avatar:
#     def __init__(self, client_repository):
#         self.client_repository = client_repository
#         self.mmb_activated = False
#         self.alt_activated = False
#         self.ctrl_activated = False
#         self.freelook_activated = False
#         self.freelook_distance = 8
#         self.drone = DistributedSmoothActor(self.client_repository)
#         self.boom_arm = Cylinder((0,0,0),np.array([self.freelook_distance,0,0]),.1,render)
#         self.value_selector = FiniteRepetitionSelector("*", 2)
#
#         self.client_repository.createDistributedObject(distObj=self.drone, zoneId=2)
#
#         # self.floater = NodePath(PandaNode("floater"))
#         # self.floater.reparentTo(self.drone)
#         # self.floater.setZ(2.0)
#
#         # mouseWatcherNode actually also handles keyboard
#         self.isDown = base.mouseWatcherNode.is_button_down
#
#         taskMgr.add(self.move, "moveTask")
#
#         base.accept("mouse2", self.mmb_down)
#         base.accept("mouse2-up", self.mmb_up)
#         base.accept("alt", self.alt_down)
#         base.accept("alt-up", self.alt_up)
#         base.accept("ctrl", self.ctrl_down)
#         base.accept("ctrl-up", self.ctrl_up)
#         base.accept("alt-wheel_up", self.alt_wheel_up)
#         base.accept("alt-wheel_down", self.alt_wheel_down)
#
#         self.drone.start()
#
#     def alt_wheel_up(self):
#         if self.freelook_activated:
#             print(self.freelook_distance)
#             self.freelook_distance = self.value_selector.decrease_value(self.freelook_distance)
#
#     def alt_wheel_down(self):
#         if self.freelook_activated:
#             print(self.freelook_distance)
#             self.freelook_distance = self.value_selector.increase_value(self.freelook_distance)
#
#     def wheel_up(self):
#         pass
#
#     def wheel_down(self):
#         pass
#
#     def ctrl_down(self):
#         self.ctrl_activated = True
#
#     def ctrl_up(self):
#         self.ctrl_activated = False
#
#     def alt_down(self):
#         self.alt_activated = True
#
#     def alt_up(self):
#         self.alt_activated = False
#
#     def mmb_down(self):
#         self.mmb_activated = True
#
#     def mmb_up(self):
#         self.mmb_activated = False
#
#     # Accepts arrow keys to move either the player or the menu cursor,
#     # Also deals with grid checking and collision detection
#     def move(self, task):
#
#         # Get the time that elapsed since last frame.  We multiply this with
#         # the desired speed in order to find out with which distance to move
#         # in order to achieve that desired speed.
#         dt = globalClock.getDt()
#         move_speed = 7
#         # If a move-key is pressed, move drone in the specified direction.
#         # if self.isDown(KeyboardButton.asciiKey(b"w")):
#         #     self.drone.setY(self.drone, -move_speed * dt)
#         # if self.isDown(KeyboardButton.asciiKey(b"a")):
#         #     self.drone.setX(self.drone, move_speed * dt)
#         # if self.isDown(KeyboardButton.asciiKey(b"s")):
#         #     self.drone.setY(self.drone, move_speed * dt)
#         # if self.isDown(KeyboardButton.asciiKey(b"d")):
#         #     self.drone.setX(self.drone, -move_speed * dt)
#         # if self.isDown(KeyboardButton.asciiKey(b"e")):
#         #     self.drone.setZ(self.drone, move_speed * dt)
#         # if self.isDown(KeyboardButton.asciiKey(b"q")):
#         #     self.drone.setZ(self.drone, -move_speed * dt)
#         # if self.isDown(KeyboardButton.ascii_key("alt")):
#         #     print("alt clicked")
#         if self.isDown(KeyboardButton.asciiKey(b"w")):
#             self.drone.setPos(self.drone, render.getRelativeVector(self.drone, Vec3(0, 1, 0)) * move_speed * dt)
#             #self.drone.setPos(self.drone.getPos() + LVector3f(self.drone.getPos()).forward() * move_speed * dt) # render.getRelativeVector(self.drone, Vec3(0, 1, 0)).normalized()
#         # if self.isDown(KeyboardButton.asciiKey(b"s")):
#         #     self.drone.setPos(self.drone.getPos() + render.getRelativeVector(self.drone, Vec3(0, 0, -1)) * move_speed * dt)
#         #     # self.drone.setY(self.drone, move_speed * dt)
#         # if self.isDown(KeyboardButton.asciiKey(b"a")):
#         #     self.drone.setPos(self.drone.getPos() + render.getRelativeVector(self.drone, Vec3(1, 0, 0)) * move_speed * dt)
#         #     #self.drone.setX(self.drone, move_speed * dt)
#         # if self.isDown(KeyboardButton.asciiKey(b"d")):
#         #     self.drone.setPos(self.drone.getPos() + render.getRelativeVector(self.drone, Vec3(-1, 0, 0)) * move_speed * dt)
#         #     #self.drone.setX(self.drone, -move_speed * dt)
#         # if self.isDown(KeyboardButton.asciiKey(b"e")):
#         #     self.drone.setPos(self.drone.getPos() + render.getRelativeVector(self.drone, Vec3(0, 1, 0)) * move_speed * dt)
#         #     #self.drone.setZ(self.drone, move_speed * dt)
#         # if self.isDown(KeyboardButton.asciiKey(b"q")):
#         #     self.drone.setPos(self.drone.getPos() + render.getRelativeVector(self.drone, Vec3(0, -1, 0)) * move_speed * dt)
#         #     #self.drone.setZ(self.drone, -move_speed * dt)
#         #

#
#         # update distributed position and rotation (TODO: func no longer available?)
#         #self.drone.setDistPos(self.drone.getX(), self.drone.getY(), self.drone.getZ())
#         #self.drone.setDistHpr(self.drone.getH(), self.drone.getP(), self.drone.getR())
#
#         if self.alt_activated:
#             self.freelook_activated = True
#         else:
#             self.freelook_activated = False
#
#         if self.freelook_activated:
#             self.boom_arm.update((0,0,0),np.array([self.freelook_distance,0,0]),.1) # self.drone.getPos(),np.array([self.freelook_distance,0,0]),.1)#self.drone.getPos(), np.array(self.drone.getPos()) + np.array([0,self.freelook_distance,0]), 1)
#             #swap to freelook camera
#             base.camera.setPos(render.getRelativePoint(self.drone, tuple(self.boom_arm.line_end)))
#
#             new_rot = look_at_rotation(render.getRelativePoint(self.drone, tuple(self.boom_arm.line_end)), self.drone.getPos()) # TODO: camera.lookat func?
#
#             # print(new_rot)
#             # print(self.boom_arm.line_end)
#             # print(self.drone.getPos())
#             # print("\n")
#             # base.camera.setR(base.camera.getR() + 180)
#             if new_rot is not None and not np.isnan(new_rot).any():
#                 base.camera.setHpr(new_rot[2]+270, new_rot[1]+270, new_rot[0])
#
#         else:
#             rot_speed = 60
#             base.camera.setPos(self.drone.getPos())
#             if base.mouseWatcherNode.hasMouse():
#                 x = base.mouseWatcherNode.getMouseX()
#                 y = base.mouseWatcherNode.getMouseY()
#                 base.camera.setP(base.camera.getP() + y * rot_speed)
#                 self.drone.setP(base.camera.getP() + 90)
#                 if self.mmb_activated:
#                     base.camera.setR(base.camera.getR() + x * rot_speed)
#                     self.drone.setR(base.camera.getR())
#                 else:
#                     base.camera.setH(base.camera.getH() + -x * rot_speed)
#                     self.drone.setH(base.camera.getH() - 180)
#         return task.cont

class Cylinder():
    def __init__(self, line_start, line_end, line_thickness, reparent_to):
        self.line_start = np.array(line_start)
        self.line_end = np.array(line_end)
        self.line_thickness = line_thickness
        self.line_midpoint = (np.array(line_start) + np.array(line_end)) / 2.0
        self.model = loader.loadModel("models/Cylinder.bam")
        self.model.reparent_to(reparent_to)
        euler_angles = look_at_rotation(self.line_midpoint, self.line_end)
        #print(euler_angles)
        euler_angles = [x + 180 for x in euler_angles]
        #print(euler_angles)
        self.model.setPosHprScale(self.line_midpoint[0], self.line_midpoint[1], self.line_midpoint[2], euler_angles[2]+90, euler_angles[1]+270, euler_angles[0], line_thickness, line_thickness, float(np.sqrt((self.line_end - self.line_start).dot((self.line_end - self.line_start))))/2)

    def update(self, line_start, line_end, line_thickness):
        self.line_start = np.array(line_start)
        self.line_end = np.array(line_end)
        self.line_thickness = line_thickness
        self.line_midpoint = (np.array(line_start) + np.array(line_end)) / 2.0
        euler_angles = look_at_rotation(self.line_midpoint, self.line_end)
        #print(euler_angles)
        euler_angles = [x + 180 for x in euler_angles] #[x + 360 if x < 0 else x for x in euler_angles]
        #print(euler_angles) # roll, pitch, yaw
        self.model.setPosHprScale(self.line_midpoint[0], self.line_midpoint[1], self.line_midpoint[2], euler_angles[2]+90, euler_angles[1]+270, euler_angles[0], line_thickness, line_thickness, float(np.sqrt((self.line_end - self.line_start).dot((self.line_end - self.line_start))))/2)

    # def update_length(self, line_start, line_end, line_thickness):
    #     self.line_start = np.array(line_start)
    #     self.line_end = np.array(line_end)
    #     self.line_thickness = line_thickness
    #     self.line_midpoint = (np.array(line_start) + np.array(line_end)) / 2.0
    #     euler_angles = self.look_at_rotation(self.line_midpoint, self.line_end)
    #     print(euler_angles)
    #     euler_angles = [x + 180 for x in euler_angles] #[x + 360 if x < 0 else x for x in euler_angles]
    #     print(euler_angles) # roll, pitch, yaw
    #     self.model.setPosHprScale(self.line_midpoint[0], self.line_midpoint[1], self.line_midpoint[2], euler_angles[2]+90, euler_angles[1]+270, euler_angles[0], line_thickness, line_thickness, float(np.sqrt((self.line_end - self.line_start).dot((self.line_end - self.line_start))))/2)

        # self.model.setPos(self.line_midpoint[0], self.line_midpoint[1], self.line_midpoint[2])
        # self.model.setScale(line_thickness, line_thickness, float(np.sqrt((self.line_end - self.line_start).dot((self.line_end - self.line_start)))))


# TODO: Rework the syntax for the mouse hovering and clicking of objects and the keyboard input system
class MainApp(ShowBase):
    # Setup window size, title and so on
    load_prc_file_data("", """
    win-size 1920 1056
    window-title Starcel
    """)

    def __init__(self):
        self.mouse_activated = False
        def set_relative_mode_and_hide_cursor():
            props = WindowProperties()
            props.setCursorHidden(True)
            # TODO: Update to M_Relative in Panda 11.0 and replace
            props.set_mouse_mode(WindowProperties.M_confined)
            base.win.request_properties(props)

        def normal_mouse_mode():
            props = WindowProperties()
            props.setCursorHidden(False)
            props.setMouseMode(WindowProperties.M_absolute)
            base.win.requestProperties(props)

        def toggle_mouse_mode():
            if self.mouse_activated:
                self.mouse_activated = False
                drone.mouse_enabled = self.mouse_activated
                set_relative_mode_and_hide_cursor()
            else:
                self.mouse_activated = True
                drone.mouse_enabled = self.mouse_activated
                normal_mouse_mode()

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
        # base.camLens.set_near(.01)
        # self.render.set_shader_auto()
        # gltf.patch_loader(self.loader)

        # Set time of day
        self.render_pipeline.daytime_mgr.time = 0

        # initialize the client
        client = GameClientRepository()
        def clientJoined():
            # title["text"] = "Starcel (CONNECTED)"
            global drone
            drone = DroneController(client)
            drone.xrsdk = myXRSDK
            drone.mouse_enabled = self.mouse_activated
            drone.setup()


        base.accept("client-joined", clientJoined)

        #yo = DroneController(client)
        #yo.setup()

        set_relative_mode_and_hide_cursor()

        # Fonts and theme
        fontPath = "SourceCodePro-Bold.ttf"
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
                pyout = spawn_scell(text=output, pos=self.hud_bound_textNode.getPos() + (0, 0, -2))
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
        # Load files with python -m blend2bam 1.blend 2.bam
        # Transparency in .blend not working, .egg should work
        model = loader.loadModel("scene/TestScene.bam")
        model.reparent_to(render)
        model.setPos(0, 0, -10)
        model.node().setIntoCollideMask(BitMask32.bit(1))
        self.render_pipeline.prepare_scene(model)

        # Cylinder([-10, -10, -10], [10, -10, 10], .1, render)

        model2 = loader.loadModel("models/coordinate2.bam")  # y and z are flipped
        print(type(model2))
        model2.reparent_to(render)
        model2.setScale(1)
        model2.setPos(model2, 0, 0, 0)
        # model2.setTransparency(TransparencyAttrib.MAlpha)
        # model2.setTransparency(True)
        # model2.setAlphaScale(0.5)

        # pivot = NodePath('somethnig')
        # pivot.reparent_to(render)
        # #pivot.reparent_to(render)
        # #random.seed(0)
        #
        # model2 = loader.loadModel("models/DroneSphereRot.bam")  # y and z are flipped
        # model2.reparent_to(render)
        # n = 10
        #
        # global rings
        # global cubes
        # cubes = []
        # rings = []
        #
        # for z in range(1,5):
        #     ring = NodePath('somethnig2')
        #     ring.reparent_to(render)
        #     ring.setScale(z)
        #     rings.append(ring)
        #     for i in range(n):
        #         pivot.setHpr(0,i * 360 // n,0)
        #         e = loader.loadModel("models/DroneSphereRot.bam")
        #         e.reparent_to(pivot)
        #         e.setScale(.2 * z)
        #         model2.setPos(0, 0, ((z * z) + 3) * .16)
        #         #e.color = color.hsv(0, 0, z / 5 + (random.random() * .1))
        #         e.reparent_to(ring)
        #         cubes.append(e)

        # for e in cubes:
        #     e.reparent_to(render)
        # for e in rings:
        #     e.reparent_to(render)


        # model3 = loader.loadModel("models/DroneSphere.bam")
        # model3.reparent_to(render)
        # model3.setHpr(45,45,45)
        # model3.setScale(.5)
        # model3.setPos(model3, 0, -1, 0)

        model4 = loader.loadModel("models/car.bam")
        model4.reparent_to(render)
        model4.setScale(2.5)
        model4.setHpr(215, 0, 0)
        model4.set_pos(0, -25, -10.3)
        self.render_pipeline.prepare_scene(model4)

        model5 = loader.loadModel("models/DroneSphereRot.bam")
        model5.reparent_to(render)
        model5.setHpr(45,90,135)
        model5.setScale(.05)
        model5.setPos(model5.getPos() + render.getRelativeVector(model5, Vec3(0, 1, 0)).normalized()*3)

        # model = loader.loadModel("/c/Users/xnick/Downloads/panda3d-master/panda3d-master/models/panda.egg")
        # model.reparent_to(render)
        self.model6 = loader.loadModel("models/rice_bowl.glb")
        self.model6.set_scale(1.5)
        self.model6.set_pos(0,0,9)
        self.model6.reparent_to(render)

        # self.model_rice = loader.loadModel("models/ricegrain.glb")
        # self.model_rice.set_scale(1)
        # self.model_rice.reparent_to(render)

        # rotation code ported from https://github.com/pokepetter
        self.rice_rot = 0
        self.rings = []
        self.rices = []
        self.pivot = render.attachNewNode('pivot')
        num_of_rice=11
        for z in range(1,5):
            ring = render.attachNewNode('ring')
            ring.set_scale(z*3)
            self.rings.append(ring)
            for i in range(num_of_rice):
                self.pivot.set_h(i * 360 // num_of_rice)
                e = loader.loadModel("models/ricegrain.glb")
                if (z * num_of_rice) + i == 34:
                    e = loader.loadModel("models/ricegrainchrome.glb")
                    e_col = e.attachNewNode(CollisionNode('RiceColNode'))
                    e_col.node().addSolid(CollisionBox(e.getTightBounds()[0] - e.getPos(), e.getTightBounds()[1] - e.getPos()))#CollisionBox(e.getTightBounds()[0] / 50, e.getTightBounds()[1] / 50))
                e.reparent_to(self.pivot)
                e.set_x(((z * z) + 3) * .16)
                e.set_scale(max(.2 * math.pow(z,.9) *.1, .01))
                if (z * num_of_rice) + i == 34:
                    e.set_scale(e.get_scale()*10)
                old_pos = e.get_pos()
                old_pos = render.getRelativePoint(self.pivot, old_pos)
                old_scale = e.get_scale()
                #old_hpr = e.get_hpr()
                e.reparent_to(ring)#e.world_parent = ring
                #e.set_scale(old_scale)
                e.set_pos(old_pos)
                e.set_hpr(random()*360,random()*360,random()*360)
                self.rices.append(e)


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
                            print(self.pq.getEntry(0))
                        elif pickedObj.getName() == "RiceColNode":
                            os.startfile("C:\Program Files\Google\Chrome\Application\chrome.exe")
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


        self.updateTask = taskMgr.add(self.update, "update")


        def scenegraph():
            lsb = LineStream()
            render.ls(lsb)
            text = ''
            while lsb.isTextAvailable():
                text += lsb.getLine() + '\n'
            return text

        def spawn_scell(pos, text="=Testing"):
            global drone
            return SCell(drone,text=text,pos=pos)

        def spawn_scell_at_player():
            # print(self.controller.showbase.cam.get_pos(self.controller.showbase.render))
            #return spawn_scell(pos=self.controller.showbase.cam.get_pos(self.controller.showbase.render))
            return spawn_scell(pos=drone.drone.getPos())
        def esc():
            # entry['focus'] = False
            entry._d_entry.guiItem.set_focus(False)
            self.hud_bound_textNode = None
            pass

        base.accept("esc", esc)
        base.accept("m", toggle_mouse_mode)

        base.accept("=", spawn_scell_at_player)





        # # Function to put instructions on the screen.
        # def addInstructions(pos, msg):
        #     return OnscreenText(text=msg, style=1, fg=(0, 0, 0, 1), shadow=(1, 1, 1, 1),
        #                         parent=base.a2dTopLeft, align=TextNode.ALeft,
        #                         pos=(0.08, -pos - 0.04), scale=.06)

        # Function to put title on the screen.
        # def addTitle(text):
        #     return OnscreenText(text=text, style=1, pos=(-0.1, 0.09), scale=.08,
        #                         parent=base.a2dBottomRight, align=TextNode.ARight,
        #                         fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))
        #
        # title = addTitle("Starcel (NOT CONNECTED)")

        # inst1 = addInstructions(0.06, "W|A|S|D: Move avatar)")
        # inst2 = addInstructions(0.12, "esc: Close the client")
        # inst3 = addInstructions(0.24, "See console output")


    def update(self, task):
        self.rice_rot += 1
        self.model6.set_hpr(-self.rice_rot,0,0)

        for e in self.rings:
            rotation_speed = 5 - e.get_scale()[0]
            #print(rotation_speed)
            if rotation_speed > 0:
                rotation_speed = math.pow(rotation_speed, 1.5)
            e.set_h(e,rotation_speed * base.clock.getDt() * 10)#rotation_speed * globalClock.getDt() * 10)

        for e in self.rices:
            rotation_speed = 5 - e.get_parent().get_scale()[0]
            if rotation_speed > 0:
                rotation_speed = math.pow(rotation_speed, 1.5)
            e.set_hpr(e, rotation_speed * base.clock.getDt() * 20,rotation_speed * base.clock.getDt() * 20,rotation_speed * base.clock.getDt() * 20)#rotation_speed * globalClock.getDt() * 20)
        # global rings
        # global cubes
        # dt = globalClock.getDt()
        # for e in rings:
        #     rotation_speed = 5 - e.getScale()[0]e
        #     rotation_speed = math.pow(rotation_speed, 1.5)
        #     e.setHpr(e,0,rotation_speed * dt * 10,0)
        #
        # for e in cubes:
        #     rotation_speed = 5 - e.parent.getScale()[0]
        #     rotation_speed = math.pow(rotation_speed, 1.5)
        #     e.setHpr(e,Vec3(rotation_speed) * dt * 20)

        return task.cont

    ### Begin Command Processing ###
    # list(cmdix.listcommands()): arch, base64, basename, bunzip2, bzip2, cal, cat, cp, crond, diff, dirname, env, expand, gunzip, gzip, httpd, init, kill, ln, logger, ls, md5sum, mkdir, mktemp, more, mv, nl, pwd, rm, rmdir, sendmail, seq, sh, sha1sum, sha224sum, sha256sum, sha384sum, sha512sum, shred, shuf, sleep, sort, tail, tar, touch, uname, uuidgen, wc, wget, yes, zip

    # cmd = ['echo', 'I like potatos']
    # proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # o, e = proc.communicate()

    # print('Output: ' + o.decode('ascii'))
    # print('Error: '  + e.decode('ascii'))
    # print('code: ' + str(proc.returncode))
    # Linux Commands
    def ls(self,args):
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

    def man(self,args):
        print((subprocess.run(["help"], shell=True, capture_output=True, text=True).stdout))

    # Built-in commands
    def autocomplete(self,search_word):
        autocomplete = fast_autocomplete.AutoComplete(words=words)
        ac_output = []
        if search_word:
            ac_output = autocomplete.search(word=search_word[0])
        # print(ac_output)
        # return [''.join(x) for x in ac_output]
        return ['_autocomplete'] + ac_output

    def plot(self,_):
        x, y, z = np.pi * np.mgrid[-1:1:7j, -1:1:7j, -1:1:7j]
        vol = np.cos(x) + np.cos(y) + np.cos(z)
        iso_val = 0.0
        verts, faces, normals, values = marching_cubes(vol, iso_val, spacing=(0.4, 0.4, 0.4))
        return ("_vertices", [["X=%.3f" % x[0] + " Y=%.3f" % x[1] + " Z=%.3f" % x[2]] for x in verts], "_faces",
                [["X=%s" % x[0] + " Y=%s" % x[1] + " Z=%s" % x[2]] for x in faces], "_normals",
                [["X=%.3f" % x[0] + " Y=%.3f" % x[1] + " Z=%.3f" % x[2]] for x in normals])


MainApp().run()


# from rpcore.util.movement_controller import MovementController
#
# self.controller = MovementController(self)
# # self.controller.set_initial_position(
# #     Vec3(-7.5, -5.3, 1.8), Vec3(-5.9, -4.0, 1.6))
# self.controller.setup()
#
# base.accept("l", self.tour)
#
#
# def tour(self):
#     """ Camera flythrough """
#     mopath = (
#         (Vec3(-10.8645000458, 9.76458263397, 2.13306283951), Vec3(-133.556228638, -4.23447799683, 0.0)),
#         (Vec3(-10.6538448334, -5.98406457901, 1.68028640747), Vec3(-59.3999938965, -3.32706642151, 0.0)),
#         (Vec3(9.58458328247, -5.63625621796, 2.63269257545), Vec3(58.7906494141, -9.40668964386, 0.0)),
#         (Vec3(6.8135137558, 11.0153560638, 2.25509500504), Vec3(148.762527466, -6.41223621368, 0.0)),
#         (Vec3(-9.07093334198, 3.65908527374, 1.42396306992), Vec3(245.362503052, -3.59927511215, 0.0)),
#         (Vec3(-8.75390911102, -3.82727789879, 0.990055501461), Vec3(296.090484619, -0.604830980301, 0.0)),
#     )
#     self.controller.play_motion_path(mopath, 3.0)