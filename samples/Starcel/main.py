# Networked actor repos
from src.ClientRepository import GameClientRepository

from direct.showbase.ShowBase import ShowBase  # Loader
from panda3d.core import *
# from panda3d.core import Vec3, load_prc_file_data, KeyboardButton, NodePath, PandaNode, TextNode
# import gltf

import os, sys, math, socket, subprocess, cmdix, xarray as xr, numpy as np, dill
from random import random, randint, seed
from p10ga_py import *
from skimage.measure import marching_cubes
import scipy.sparse.linalg
import scipy
import time, uuid, copy, asyncio
from threading import Thread, Timer
import copy
import limeade
from character import DroneController
from textobject import SCell

import fast_autocomplete
import cmdix
import subprocess
import myfunctions

import clr
sys.path.append("C:\\Users\\xnick\\Documents\\Personal\\_git\\TCLRayneoAir2CLI\\bin\\Debug\\net7.0\\")
clr.AddReference("TCLRayneoAir2CLI")
# print(clr._available_namespaces)
from FfalconXR import XRSDK  # syntax highlighter may not highlight errors
myXRSDK = XRSDK()
# print(dir(XRSDK))
myXRSDK.XRSDK_Init()  # The purpose of this is to get the four quaternion values from the AR glasses.

# Change to the current directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

global drone


# TODO: Rework the syntax for the mouse hovering, clicking of objects, and the keyboard input system to be more human-oriented
class MainApp(ShowBase):  # Client
    # Setup window size, title and so on
    load_prc_file_data("", """
    win-size 1600 900
    window-title Starcel
    """)  # fullscreen #t # be sure to update window size when changing to fullscreen

    def __init__(self):
        # Collect all Words/Function/Command/Formula/Script/Action/Verb/Alias/Procedure/Algorithm Names
        def get_available_functions():
            # load aliases from csv into xarray, xarray has netcdf format, which is built on hdf5 format.
            # These are the best formats for storing and interfacing with multidimensional data
            # TODO: Wrap API for xarray to be natural
            aliasfunctions = xr.DataArray(
                np.loadtxt("aliasfunctions.csv",  # it is important to understand that no field is required to be filled out
                           delimiter=",", dtype=str))
            available_functions = aliasfunctions.isel(dim_1=0)[1:]
            # print([func.split('/') for func in available_functions])
            # for function in np.array(available_functions):
            #     print("'" + function + "'" + ",")
            flat_list = [item for sublist in [func.split('/') for func in np.array(available_functions)] for item in sublist]  # Recall that a slash is simply a delimiter, just as the border between two spreadsheet cells
            return flat_list

        # Render Pipeline setup
        pipeline_path = "../../"
        sys.path.insert(0, pipeline_path)

        from rpcore import RenderPipeline, SpotLight
        # from rpcore.util.movement_controller import MovementController

        self.render_pipeline = RenderPipeline()
        self.render_pipeline.create(self)
        # self.render.set_shader_auto()

        # Set time of day
        self.render_pipeline.daytime_mgr.time = 0

        # Initialize the client
        client = GameClientRepository()
        def clientJoined():
            global drone
            drone = DroneController(client)
            drone.render_pipeline = self.render_pipeline
            drone.xrsdk = myXRSDK
            drone.mouse_enabled = self.mouse_activated
            drone.setup()

        base.accept("client-joined", clientJoined)

        # Scene Setup
        # Convert blender files to bam files using python -m blend2bam TestScene.blend TestScene.bam
        model = loader.loadModel("scene/TestScene.bam")  # The ":pgraphnodes(error): PointLight" error message is a minor issue with one of the objects
        model.reparent_to(render)
        model.setPos(0, 0, 0)
        model.node().setIntoCollideMask(BitMask32.bit(1))
        self.render_pipeline.prepare_scene(model)

        rice_grain_model = loader.loadModel("models/ricegrainchrome.glb")
        rice_grain_model.reparent_to(render)
        rice_grain_model_col = rice_grain_model.attachNewNode(CollisionNode('RiceColNode'))
        rice_grain_model_col.node().addSolid(CollisionBox(rice_grain_model.getTightBounds()[0] - rice_grain_model.getPos(), rice_grain_model.getTightBounds()[1] - rice_grain_model.getPos()))
        
        self.ambientLight = self.render.attachNewNode(AmbientLight('ambient'))
        self.ambientLight.node().setColor((0.1, 0.1, 0.1, 1))
        self.render.setLight(self.ambientLight)

        # Keyboard Functions: functions that run on specific keyboard keys
        def set_relative_mode_and_hide_cursor():
            props = WindowProperties()
            props.setCursorHidden(True)
            # TODO: Update to M_Relative in Panda 11.0
            props.set_mouse_mode(WindowProperties.M_confined)
            base.win.request_properties(props)

        set_relative_mode_and_hide_cursor()

        def normal_mouse_mode():
            props = WindowProperties()
            props.setCursorHidden(False)
            props.setMouseMode(WindowProperties.M_absolute)
            base.win.requestProperties(props)

        self.mouse_activated = False
        def toggle_mouse_mode():
            global drone
            if self.mouse_activated:
                self.mouse_activated = False
                drone.mouse_enabled = self.mouse_activated
                base.win.movePointer(0, int(base.win.getXSize() / 2), int(base.win.getYSize() / 2))
                drone.update_mouse_offsets()
                set_relative_mode_and_hide_cursor()
            else:
                self.mouse_activated = True
                drone.mouse_enabled = self.mouse_activated
                base.win.movePointer(0, int(base.win.getXSize() / 2), int(base.win.getYSize() / 2))
                drone.update_mouse_offsets()
                normal_mouse_mode()

        def spawn_scell(pos, text="ls(None)"): # mypythoncmdfuncs.MyPythonCMDFuncs().desktop()
            global drone
            return SCell(drone,text=text,pos=pos)

        self.current_scell = None
        self.scells = {}
        def spawn_scell_at_player():
            global drone
            self.current_scell = spawn_scell(pos=drone.drone.getPos())

            self.scells.update({self.current_scell.collision_node.getName(): self.current_scell})
            return self.current_scell

        def esc():
            if self.current_scell is not None:
                self.current_scell.cursor.cursor_shown = False
                self.current_scell.most_recent_owner.keyboard_capturer.set_active_scell(None)
            pass

        self.fullscreen = False
        def fullscreen():
            if not self.fullscreen:
                self.fullscreen = True
                wp = WindowProperties()
                wp.set_size(1600,900)
                wp.setFullscreen(1)
                base.win.requestProperties(wp)
            else:
                self.fullscreen = False
                wp = WindowProperties()
                wp.setFullscreen(0)
                base.win.requestProperties(wp)

        def tour():  # Camera fly through
            mopath = (
                (Vec3(-10.8645000458, 9.76458263397, 2.13306283951), Vec3(-133.556228638, -4.23447799683, 0.0)),
                (Vec3(-10.6538448334, -5.98406457901, 1.68028640747), Vec3(-59.3999938965, -3.32706642151, 0.0)),
                (Vec3(9.58458328247, -5.63625621796, 2.63269257545), Vec3(58.7906494141, -9.40668964386, 0.0)),
                (Vec3(6.8135137558, 11.0153560638, 2.25509500504), Vec3(148.762527466, -6.41223621368, 0.0)),
                (Vec3(-9.07093334198, 3.65908527374, 1.42396306992), Vec3(245.362503052, -3.59927511215, 0.0)),
                (Vec3(-8.75390911102, -3.82727789879, 0.990055501461), Vec3(296.090484619, -0.604830980301, 0.0)),
            )
            drone.play_motion_path(mopath, 3.0)


        base.accept("m", toggle_mouse_mode)

        base.accept("=", spawn_scell_at_player)

        base.accept("esc", esc)

        base.accept("f11", fullscreen)

        base.accept("t", tour)

        def submit_scell():
            if base.mouseWatcherNode.is_button_down(KeyboardButton.shift()):
                print("submit_scell clicked")
                global drone
                function_classes = []
                # function_classes.append([func for func in reversed(list(globals().keys())) if not func.startswith('__')])
                # function_classes.append(locals())
                function_classes.append([func for func in reversed(list(dir(mypythoncmdfuncs.MyPythonCMDFuncs))) if not func.startswith('__')])
                # function_classes.append(list(cmdix.listcommands()))
                # function_classes.append(get_available_functions())

                print(function_classes)

                words = {}
                for key in sum(function_classes, []):  # flatten
                    words[key] = {}

                def autocomplete(words, search_word):
                    autocomplete = fast_autocomplete.AutoComplete(words=words)
                    ac_output = []
                    if search_word:
                        ac_output = autocomplete.search(word=search_word[0])
                    # return [''.join(x) for x in ac_output]
                    return ac_output

                print(autocomplete(words, self.current_scell.text.get_text()))

                output = None

                drone.stdout_handler.last_output = ""
                input_text = self.current_scell.text.get_text()
                parsed = input_text.strip().split(' ')
                if parsed[0] == "cd":
                    if parsed[1] == "..":
                        os.chdir(os.path.dirname(os.getcwd()))
                        print(os.getcwd())
                    else:
                        os.chdir(input_text.replace("cd "))
                        print(os.getcwd())
                elif parsed[0] in list(cmdix.listcommands()):  # linux commands
                    output = cmdix.runcommandline(input_text)
                elif ".exe" in parsed[0]:
                    cmdstring = [input_text]
                    self.dlp = subprocess.Popen(
                        cmdstring,
                        stdin=subprocess.PIPE,
                        bufsize=-1,
                        shell=False,
                    )
                elif ((parsed[0]) in function_classes):  # functions defined in this file
                    print("customfunc called")
                    # output = locals()
                else:
                    try:
                        # print("Executing of received statement: " + input_text.strip())
                        output = exec(input_text.strip())  # Executing of received statement. Exec relies on the stdout print statements to receive output whereas eval would assign the output of the received statement
                        print(output)
                        # output = repr(self.stdout_handler.last_output)
                    except Exception as e:
                        output = e

                try:
                    if not str(output) or output is None or output == "":
                        output = repr(drone.stdout_handler.last_output)
                except:
                    pass

                try:
                    pyout = SCell(drone, text=output, pos=self.current_scell.textNode.getPos() + self.current_scell.textNode.getTightBounds()[1] + (0, 0, -2))
                except:
                    pass

        base.accept("enter", submit_scell)  # shift-enter doesn't work, so shift is added as an if condition

        # collision_debugger = CollisionVisualizer("debug")
        # collision_debugger.reparent_to(render)
        # render.attachNewNode(collision_debugger)
        self.picker = CollisionTraverser()
        # self.picker.showCollisions(render)
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
            # limeade.refresh()
            # check if we have access to the mouse
            if base.mouseWatcherNode.hasMouse():
                # get the mouse position
                mpos = base.mouseWatcherNode.getMouse()
                pos3d = LPoint3f()
                nearPoint = LPoint3f()
                farPoint = LPoint3f()
                base.camLens.extrude(mpos, nearPoint, farPoint)
                # set the position of the ray based on the mouse position
                self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
                self.picker.traverse(render)
                # if we have hit something sort the hits so that the closest is first and highlight the node
                if self.pq.getNumEntries() > 0:
                    self.pq.sortEntries()
                    # click_pos = # pickerNode.getSolid(0).origin #.direction.normalized()
                    try:
                        pickedObj = self.pq.getEntry(0).getIntoNodePath()
                        hit_pos = self.pq.getEntry(0).get_surface_point(self.render)
                        print(hit_pos)  # click position
                        if "TextColNode" in pickedObj.getName():
                            self.current_scell = self.scells.get(pickedObj.getName())
                            self.current_scell.cursor.get_click_coordinates(hit_pos)
                            self.current_scell.cursor.cursor_shown = True
                            self.current_scell.most_recent_owner.keyboard_capturer.set_active_scell(self.current_scell)  # TODO: Fix all that dirty code, lol
                        elif "RiceColNode" in pickedObj.getName():
                            os.startfile("C:\Program Files\Google\Chrome\Application\chrome.exe")
                        elif "IconColNode" in pickedObj.getName():
                            os.startfile(mypythoncmdfuncs.allicons[pickedObj.getName()].url)
                        else:
                            self.win.getProperties().getForeground()
                            self.current_scell.most_recent_owner.keyboard_capturer.set_active_scell(None)
                            self.current_scell.cursor.cursor_shown = False
                    except:
                        pass
                else:
                    self.win.getProperties().getForeground()
                    if self.current_scell is not None:
                        self.current_scell.most_recent_owner.keyboard_capturer.set_active_scell(None)
                        self.current_scell.cursor.cursor_shown = False

        # self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')
        self.accept("mouse1", mouseTask)

        # def onWindowEvent():

        # self.accept(base.win.getWindowEvent(), onWindowEvent)

        self.updateTask = taskMgr.add(self.update, "update")


    def update(self, task):
        return task.cont


MainApp().run()