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
import time, uuid, copy, asyncio
from threading import Thread, Timer

# Change to the current directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# initialize the engine
# base = ShowBase()

#base.disableMouse()


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
    def __init__(self, cr):
        self.cr = cr
        self.ralph = DistributedSmoothActor(self.cr)

        self.cr.createDistributedObject(distObj=self.ralph, zoneId=2)

        # Create a floater object, which floats 2 units above ralph.  We
        # use this as a target for the camera to look at.

        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.ralph)
        self.floater.setZ(2.0)

        # We will use this for checking if keyboard keys are pressed
        self.isDown = base.mouseWatcherNode.isButtonDown

        taskMgr.add(self.move, "moveTask")

        # Set up the camera
        base.camera.setPos(self.ralph.getX(), self.ralph.getY() + 10, 2)

        # start the avatar
        self.ralph.start()

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        # Get the time that elapsed since last frame.  We multiply this with
        # the desired speed in order to find out with which distance to move
        # in order to achieve that desired speed.
        dt = globalClock.getDt()

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        if self.isDown(KeyboardButton.asciiKey(b"j")):
            base.camera.setX(base.camera, -20 * dt)
        if self.isDown(KeyboardButton.asciiKey(b"k")):
            base.camera.setX(base.camera, +20 * dt)

        # If a move-key is pressed, move ralph in the specified direction.

        if self.isDown(KeyboardButton.asciiKey(b"a")):
            self.ralph.setH(self.ralph.getH() + 300 * dt)
        if self.isDown(KeyboardButton.asciiKey(b"d")):
            self.ralph.setH(self.ralph.getH() - 300 * dt)
        if self.isDown(KeyboardButton.asciiKey(b"w")):
            self.ralph.setY(self.ralph, -20 * dt)
        if self.isDown(KeyboardButton.asciiKey(b"s")):
            self.ralph.setY(self.ralph, +10 * dt)

        # update distributed position and rotation
        # self.ralph.setDistPos(self.ralph.getX(), self.ralph.getY(), self.ralph.getZ())
        # self.ralph.setDistHpr(self.ralph.getH(), self.ralph.getP(), self.ralph.getR())

        # If ralph is moving, loop the run animation.
        # If he is standing still, stop the animation.
        currentAnim = self.ralph.getCurrentAnim()

        if self.isDown(KeyboardButton.asciiKey(b"w")):
            pass
            #if currentAnim != "run":
                #self.ralph.loop("run")
        elif self.isDown(KeyboardButton.asciiKey(b"s")):
            # Play the walk animation backwards.
            #if currentAnim != "walk":
                #self.ralph.loop("walk")
            self.ralph.setPlayRate(-1.0, "walk")
        elif self.isDown(KeyboardButton.asciiKey(b"a")) or self.isDown(KeyboardButton.asciiKey(b"d")):
            #if currentAnim != "walk":
                #self.ralph.loop("walk")
            self.ralph.setPlayRate(1.0, "walk")
        else:
            if currentAnim is not None:
                #self.ralph.stop()
                #self.ralph.pose("walk", 5)
                self.isMoving = False

        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.

        camvec = self.ralph.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            base.camera.setPos(base.camera.getPos() + camvec * (camdist - 10))
            camdist = 10.0
        if camdist < 5.0:
            base.camera.setPos(base.camera.getPos() - camvec * (5 - camdist))
            camdist = 5.0

        # The camera should look in ralph's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above ralph's head.
        base.camera.lookAt(self.floater)

        return task.cont


class MainApp(ShowBase):


    # Setup window size, title and so on
    load_prc_file_data("", """
    win-size 1920 1056
    window-title Starcel
    """)

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
            flat_list = [item for sublist in [func.split('/') for func in np.array(available_functions)] for item in
                         sublist]
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
            return spawn_scell(pos=Avatar().ralph.getPos())

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


    # def pythonusemefix(): #not meant for use, tricks the interpreter to loading these funcs in locals
    # man("_")
    # ls("_")
    # scenegraph("_")

    # pythonusemefix()

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


# base.accept("escape", exit)



# start the client
#base.run()
