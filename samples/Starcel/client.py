# Networked actor repos
from ClientRepository import GameClientRepository

from direct.showbase.ShowBase import ShowBase  # Loader
from panda3d.core import *
# from panda3d.core import Vec3, load_prc_file_data, KeyboardButton, NodePath, PandaNode, TextNode
# import gltf

# import direct.directbase.DirectStart
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from inputfield import InputField

import os, sys, math, socket, subprocess, cmdix, xarray as xr, numpy as np, fast_autocomplete, dill
from random import random, randint, seed
from p10ga_py import *
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
# XRSDK setup and a small reminder of how much brute-forcing went into every development step of this program
# clr.AddReference('C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLIBroadcaster\\TCLRayneoAir2CLIBroadcaster.sln')
# clr.AddReference('C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLIBroadcaster\\TCLRayneoAir2CLIBroadcaster')
# clr.AddReference('C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLIBroadcaster\\XRSDK.dll')
# clr.AddReference("C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLIBroadcaster\\bin\Debug\\net6.0\\TCLRayneoAir2CLIBroadcaster.dll")
# clr.AddReference("C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLIBroadcaster\\bin\Debug\\net6.0\\)
sys.path.append("C:\\Users\\xnick\\source\\repos\\TCLRayneoAir2CLI\\bin\\Debug\\net7.0\\")
clr.AddReference("TCLRayneoAir2CLI")
# print(clr._available_namespaces)
from FfalconXR import XRSDK  # syntax highlighter may not highlight errors

myXRSDK = XRSDK()
# print(dir(XRSDK))
myXRSDK.XRSDK_Init()

# Change to the current directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

global drone





# TODO: Rework the syntax for the mouse hovering, clicking of objects, and the keyboard input system
class MainApp(ShowBase):
    # Setup window size, title and so on
    load_prc_file_data("", """
    win-size 1600 900
    window-title Starcel
    """) # fullscreen #t # be sure to update window size when changing to fullscreen

    def __init__(self):
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
        words = {}  # Words/Function/Command/Formula/Script/Action/Verb/Alias/Procedure/Algorithm Name
        for key in getalias():
            words[key] = {}

        def autocomplete(words, search_word):
            autocomplete = fast_autocomplete.AutoComplete(words=words)
            ac_output = []
            if search_word:
                ac_output = autocomplete.search(word=search_word[0])
            # print(ac_output)
            # return [''.join(x) for x in ac_output]
            return ['_autocomplete'] + ac_output

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
            global drone
            drone = DroneController(client)
            drone.render_pipeline = self.render_pipeline
            drone.xrsdk = myXRSDK
            drone.mouse_enabled = self.mouse_activated
            drone.setup()


        base.accept("client-joined", clientJoined)

        # Scene Setup
        # Load test scene
        # Load files with python -m blend2bam 1.blend 2.bam
        # Transparency in .blend not working, .egg should work
        model = loader.loadModel("scene/TestScene.bam")
        model.reparent_to(render)
        model.setPos(0, 0, -10)
        model.node().setIntoCollideMask(BitMask32.bit(1))
        self.render_pipeline.prepare_scene(model)

        model2 = loader.loadModel("models/coordinate2.bam")  # y and z are flipped
        print(type(model2))
        model2.reparent_to(render)
        model2.setScale(1)
        model2.setPos(model2, 0, 0, 0)

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

        self.model6 = loader.loadModel("models/rice_bowl.glb")
        self.model6.set_scale(1.5)
        self.model6.set_pos(0,0,9)
        self.model6.reparent_to(render)

        # # rotation code ported from https://github.com/pokepetter
        # self.rice_rot = 0
        # self.rings = []
        # self.rices = []
        # self.pivot = render.attachNewNode('pivot')
        # num_of_rice=11
        # for z in range(1,5):
        #     ring = render.attachNewNode('ring')
        #     ring.set_scale(z*3)
        #     self.rings.append(ring)
        #     for i in range(num_of_rice):
        #         self.pivot.set_h(i * 360 // num_of_rice)
        #         rice_grain_model = loader.loadModel("models/ricegrain.glb")
        #         if (z * num_of_rice) + i == 34:
        #             rice_grain_model = loader.loadModel("models/ricegrainchrome.glb")
        #             rice_grain_model_col = rice_grain_model.attachNewNode(CollisionNode('RiceColNode'))
        #             rice_grain_model_col.node().addSolid(CollisionBox(rice_grain_model.getTightBounds()[0] - rice_grain_model.getPos(), rice_grain_model.getTightBounds()[1] - rice_grain_model.getPos()))#CollisionBox(e.getTightBounds()[0] / 50, e.getTightBounds()[1] / 50))
        #         rice_grain_model.reparent_to(self.pivot)
        #         rice_grain_model.set_x(((z * z) + 3) * .16)
        #         rice_grain_model.set_scale(max(.2 * math.pow(z,.9) *.1, .01))
        #         if (z * num_of_rice) + i == 34:
        #             rice_grain_model.set_scale(rice_grain_model.get_scale()*10)
        #         old_pos = rice_grain_model.get_pos()
        #         old_pos = render.getRelativePoint(self.pivot, old_pos)
        #         old_scale = rice_grain_model.get_scale()
        #         #old_hpr = e.get_hpr()
        #         rice_grain_model.reparent_to(ring)#e.world_parent = ring
        #         #e.set_scale(old_scale)
        #         rice_grain_model.set_pos(old_pos)
        #         #rice_grain_model.set_hpr(random()*360,random()*360,random()*360)
        #         self.rices.append(rice_grain_model)


        self.ambientLight = self.render.attachNewNode(AmbientLight('ambient'))
        self.ambientLight.node().setColor((0.1, 0.1, 0.1, 1))
        self.render.setLight(self.ambientLight)


        self.mouse_activated = False
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

        def spawn_scell(pos, text="="):
            global drone
            return SCell(drone,text=text,pos=pos)


        self.scells = {}
        def spawn_scell_at_player():
            # print(self.controller.showbase.cam.get_pos(self.controller.showbase.render))
            #return spawn_scell(pos=self.controller.showbase.cam.get_pos(self.controller.showbase.render))
            self.current_TextNode = spawn_scell(pos=drone.drone.getPos())

            self.scells.update({self.current_TextNode.collision_node.getName(): self.current_TextNode})
            return self.current_TextNode

        def esc():
            # entry['focus'] = False
            # entry._d_entry.guiItem.set_focus(False)
            # self.hud_bound_textNode = None
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
                # load_prc_file_data("", "fullscreen #t")
            else:
                self.fullscreen = False
                wp = WindowProperties()
                wp.setFullscreen(0)
                base.win.requestProperties(wp)
                # load_prc_file_data("", "fullscreen #f")

        def tour():
            # Camera flythrough
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

        def submit_scell(text):
            output = None

            # Put this here to comply with local scope. Perhaps this should be replaced with globals or restructured into its own file
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
                    output = exec(input_text)  # Executing of receieved statement. Exec relies on the stdout print statements to receive output whereas when this is switched to eval, output is sent back over the socket
                    # output = repr(self.stdout_handler.last_output)
                    # print(self.stdout_handler.last_output)
                except Exception as e:
                    output = e

            try:
                if not str(output) or output is None or output == "":
                    output = repr(self.stdout_handler.last_output)
            except:
                pass

            try:
                print(self.hud_bound_textNode.node())
                # self.hud_bound_textNode.node().setText(output)
                pyout = spawn_scell(text=output, pos=self.hud_bound_textNode.getPos() + (0, 0, -2))
                t = Timer(.02, lambda a, b: a.node().setText(b), (pyout, output,))
                t.start()
                print(self.hud_bound_textNode.node())
            except:
                pass
            # self.pyout.node().setText(output)
            # time.sleep(2)

        # base.accept("shift-enter", submit_scell)


        # collisiondebugger = CollisionVisualizer("debug")
        # collisiondebugger.reparent_to(render)
        # render.attachNewNode(collisiondebugger)
        # self.render_pipeline.prepare_scene(model)

        # Setup Collision
        # CollisionTraverser and a Collision Handler is set up
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

        self.current_scell = None
        def mouseTask():
            print('mouse click')
            #limeade.refresh()
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
                        print(hit_pos)
                        #print(self.pq.getEntry(0).getSurfacePoint(pickedObj))
                        #print(pickedObj)
                        # click_plane = Plane(pickedObj.getTightBounds()[0] - pickedObj.getPos(),
                        #       pickedObj.getTightBounds()[1] - pickedObj.getPos())
                        # if click_plane.intersectsLine(pos3d, render.getRelativePoint(camera, nearPoint),  render.getRelativePoint(camera, farPoint)):
                        #     print("intersected at " + str(pos3d))
                        if pickedObj.getName() == "TextColNode":
                            # if self.current_textNode.textNode.equals(pickedObj.getParent().node()):
                            #     self.current_textNode
                            # self.hud_bound_textNode = pickedObj.getParent()
                            # pickedObj.get_tag("textnode")
                            # self.current_textNode = pickedObj.getParent().node()
                            self.current_scell = self.scells.get(pickedObj.getName()) # self.current_textNode.get_python_tag("object")
                            # self.current_scell.focused = True
                            self.current_scell.cursor.get_click_coordinates(hit_pos)
                            self.current_scell.cursor.cursor_shown = True

                            self.current_scell.most_recent_owner.keyboard_capturer.set_active_scell(self.current_scell)  # TODO: Fix all that dirty code, lol
                        elif pickedObj.getName() == "RiceColNode":
                            os.startfile("C:\Program Files\Google\Chrome\Application\chrome.exe")
                        else:
                            self.win.getProperties().getForeground()
                            #entry._d_entry.guiItem.set_focus(False)
                            self.current_scell.most_recent_owner.keyboard_capturer.set_active_scell(None)
                            self.current_scell.cursor.cursor_shown = False
                            # entry['focus'] = False
                            hud_bound_textNode = None
                    except:
                        pass
                else:
                    # self.controller.setup()
                    self.win.getProperties().getForeground()
                    #entry._d_entry.guiItem.set_focus(False)
                    # entry['focus'] = False
                    # self.hud_bound_textNode = None
                    if self.current_scell is not None:
                        self.current_scell.most_recent_owner.keyboard_capturer.set_active_scell(None)
                        self.current_scell.cursor.cursor_shown = False

        # self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')
        self.accept("mouse1", mouseTask)

        # def onWindowEvent():

        # self.accept(base.win.getWindowEvent(), onWindowEvent)


        self.updateTask = taskMgr.add(self.update, "update")


    # Main Update Loop
    def update(self, task):

        return task.cont


MainApp().run()