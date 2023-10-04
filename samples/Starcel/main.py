import os, sys
import math
from random import random, randint, seed
# from panda3d.core import Vec3, load_prc_file_data
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.showbase import Loader
import gltf

# import direct.directbase.DirectStart
# from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *

from inputfield import InputField

import os, sys, socket, subprocess, cmdix, xarray as xr, numpy as np, fast_autocomplete #, dill
#from p10ga_py import *
from skimage.measure import marching_cubes
import scipy.sparse.linalg
import time, uuid, copy, asyncio
from threading import Thread, Timer

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
            #print("does this work?")
            self.last_output+= data
            self._handled_stdout.write(data)

    def end(self):
        sys.stdout = self._handled_stdout
    
    def flush(self):
        self._handled_stdout.flush()



class MainApp(ShowBase):
    # Setup window size, title and so on
    load_prc_file_data("", """
    win-size 1920 1056
    window-title Starcel
    """)
    def __init__(self):
        def getalias():
            # load aliases from csv into xarray
            aliasfunctions = xr.DataArray(np.loadtxt("C:/Users/xnick/Documents/Unreal Projects/starcel/Content/SCfiles/data/aliasfunctions.csv", delimiter=",", dtype=str))
            available_functions = aliasfunctions.isel(dim_1=0)[1:]
            #print([func.split('/') for func in available_functions])
            for function in np.array(available_functions):
                print("'" + function + "'" + ",")
            flat_list = [item for sublist in [func.split('/') for func in np.array(available_functions)] for item in sublist]
            return flat_list #available_functions
        
        #Collect all aliases
        #test_keys = np.array(getalias()).tolist()
        #print(test_keys)
        words = {}
        for key in getalias():
            words[key] = {}

        #stdout handler so it cant be sent over tcp
        self.stdout_handler = StdoutHandler()
        self.stdout_handler.start()

        # Render Pipeline setup
        pipeline_path = "../../"

        sys.path.insert(0, pipeline_path)
        
        from rpcore import RenderPipeline, SpotLight
        from rpcore.util.movement_controller import MovementController
        
        self.render_pipeline = RenderPipeline()
        self.render_pipeline.create(self)     
        #self.render.set_shader_auto()
        # gltf.patch_loader(self.loader)

        # Set time of day
        self.render_pipeline.daytime_mgr.time = 0


        # Init movement controller
        self.controller = MovementController(self)
        self.controller.setup()

        # Fonts and theme
        fontPath = "SourceCodePro-Regular.ttf"
        font = loader.loadFont(fontPath, color = (1,1,1,1), renderMode = TextFont.RMSolid)
        font2 = loader.loadFont(fontPath, color = (1,1,1,1))

        # HUD setup
        self.hud_bound_textNode = None
        #callback function to set text
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
            if parsed[0] in list(cmdix.listcommands()): # linux commands
                output = cmdix.runcommandline(input_text)
            elif ((parsed[0]) in locals().keys()): # functions defined in this file
                print("customfunc called")
                output = locals()[parsed[0]](parsed[1:]) # TODO: Support for no argument functions 
            else:
                #print("eval called")
                try:
                    output = exec(input_text) # Executing of receieved statement. Exec relies on the stdout print statements to receive output whereas when this is switched to eval, output is sent back over the socket 
                    #output = repr(self.stdout_handler.last_output)
                    #print(self.stdout_handler.last_output)
                except Exception as e:
                    output = e

            try:
                if not str(output) or output is None or output == "":
                    #print("FFFF" + stdout_handler.last_output)
                    output = repr(self.stdout_handler.last_output)
                    #t.start()
                    # if output is None or output == "":
                        #output = self.tempoutput
            except:
                pass

            try:
                print(self.hud_bound_textNode.node())
                #self.hud_bound_textNode.node().setText(output)
                pyout = spawn_scell(output, self.hud_bound_textNode.getPos() + (0,0,-2))
                t = Timer(.02, fix_pyout3dtext, (pyout, output,))
                t.start()
                #thread = Thread(target = spawn_scell, args = (output, self.hud_bound_textNode.getPos() + (0,0,-2),), daemon=True)
                #thread.start()
                #thread.join()
                print(self.hud_bound_textNode.node())
                #fix_pyout3dtext(pyout, output)
            except:
                pass
            #self.pyout.node().setText(output)
            # time.sleep(2)
            
        # base.accept("shift-enter", submit_scell)
        

        # Define a function that will be called when committing the entry text
        def on_commit_func(text, field_name):
            print(f"The following has been entered into {field_name}:", text)
            submit_scell(text)

        def on_keystroke(text):          
            if self.hud_bound_textNode is not None:
                try:
                    #render.ls()
                    #print(self.hud_bound_textNode)
                    self.hud_bound_textNode.node().setText(entry._edited_text)
                    self.hud_bound_textNode.node().forceUpdate()
                    self.hud_bound_textNode.getChild(0).node().clearSolids()
                    #print(self.hud_bound_textNode.getChild(0).node())
                    self.hud_bound_textNode.getChild(0).node().addSolid(CollisionBox(self.hud_bound_textNode.getTightBounds()[0] - self.hud_bound_textNode.getPos(), self.hud_bound_textNode.getTightBounds()[1] - self.hud_bound_textNode.getPos()))
                except:
                    pass
                #print("HUD:", entry._edited_text)

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
        model.setPos(0,0,-10)
        model.node().setIntoCollideMask(BitMask32.bit(1))

        # model = loader.loadModel("/c/Users/xnick/Downloads/panda3d-master/panda3d-master/models/panda.egg")
        # model.reparent_to(render)

        self.ambientLight = self.render.attachNewNode(AmbientLight('ambient'))
        self.ambientLight.node().setColor((0.1, 0.1, 0.1, 1))
        self.render.setLight(self.ambientLight)

        #collisiondebugger = CollisionVisualizer("debug")
        #collisiondebugger.reparent_to(render)
        #render.attachNewNode(collisiondebugger)
        #self.render_pipeline.prepare_scene(model)

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
        #textNode.setH(textNode, 30)
        #textNode.setP(textNode, 30)
        
        # Setup Collision
        # CollisionTraverser and a Collision Handler is set up
        self.picker = CollisionTraverser()
        self.picker.showCollisions(render)
        self.pq = CollisionHandlerQueue() 

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))#BitMask32.bit(1))
        # self.box.setCollideMask(BitMask32.bit(1)) 
        
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP,self.pq)

        def mouseTask():
            print('mouse click')
            # check if we have access to the mouse
            if base.mouseWatcherNode.hasMouse():

                # get the mouse position
                mpos = base.mouseWatcherNode.getMouse()

                # set the position of the ray based on the mouse position
                self.pickerRay.setFromLens(base.camNode,mpos.getX(),mpos.getY())
                self.picker.traverse(render)
                # if we have hit something sort the hits so that the closest is first and highlight the node
                if self.pq.getNumEntries() > 0:
                    self.pq.sortEntries()
                    try:
                        pickedObj = self.pq.getEntry(0).getIntoNodePath()
                        print(pickedObj     )
                        if pickedObj.getName() == "TextColNode":
                            self.hud_bound_textNode = pickedObj.getParent()
                            entry._d_entry.guiItem.set_focus(True)
                            
                            #print("B" + self.hud_bound_textNode.node().text)
                            entry._d_entry.set(self.hud_bound_textNode.node().text)
                            #print(self.pq.getEntry(0))
                            
                        else: 
                            self.win.getProperties().getForeground()
                            entry._d_entry.guiItem.set_focus(False)
                            #entry['focus'] = False
                            hud_bound_textNode = None
                    except: 
                        pass
                else:
                    #print("G")
                    self.controller.setup()
                    self.win.getProperties().getForeground()
                    entry._d_entry.guiItem.set_focus(False)
                    #entry['focus'] = False
                    self.hud_bound_textNode = None
            
        #self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')
        self.accept("mouse1", mouseTask)

        def spawn_scell_at_player():
            # print(self.controller.showbase.cam.get_pos(self.controller.showbase.render))
            return spawn_scell(pos=self.controller.showbase.cam.get_pos(self.controller.showbase.render))
        
        def spawn_scell(input_text="=", pos=(0,0,0)):
            print("equal clicked")
            text = TextNode('Text' + str(uuid.uuid4()))
            text.setText(input_text)
            text.setFont(font)
            text.setAlign(TextNode.ALeft)
            textNode = render.attachNewNode(text) #text.generate()
            #textNode.getChild(0).node().setIntoCollideMask(BitMask32.bit(1))
            # textNode.setScale(50)
            textNode.setPos(pos)
            textNode.setScale(1,.1,1)
            textNode.node().setIntoCollideMask(BitMask32.bit(1))

            fromObject = textNode.attachNewNode(CollisionNode('TextColNode'))
            #fromObject.show()
            #print(textNode.getTightBounds())
            fromObject.node().addSolid(CollisionBox(textNode.getTightBounds()[0] - textNode.getPos(), textNode.getTightBounds()[1] - textNode.getPos()))
            try:
                entry._d_entry.set(textNode.node().text)
            except:
                pass
            #print(len(entry._edited_text))
            entry._d_entry.guiItem.set_focus(True)
            entry._d_entry.setCursorPosition(len(entry._edited_text))
            self.hud_bound_textNode = textNode
            #print(textNode)
            return textNode
        
        base.accept("=", spawn_scell_at_player)

        def esc():
            #entry['focus'] = False
            entry._d_entry.guiItem.set_focus(False)
            self.hud_bound_textNode = None
            pass

        base.accept("esc", esc)

    ### Begin Command Processing ### 
    # list(cmdix.listcommands()): arch, base64, basename, bunzip2, bzip2, cal, cat, cp, crond, diff, dirname, env, expand, gunzip, gzip, httpd, init, kill, ln, logger, ls, md5sum, mkdir, mktemp, more, mv, nl, pwd, rm, rmdir, sendmail, seq, sh, sha1sum, sha224sum, sha256sum, sha384sum, sha512sum, shred, shuf, sleep, sort, tail, tar, touch, uname, uuidgen, wc, wget, yes, zip


    #cmd = ['echo', 'I like potatos']
    #proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #o, e = proc.communicate()

    #print('Output: ' + o.decode('ascii'))
    #print('Error: '  + e.decode('ascii'))
    #print('code: ' + str(proc.returncode))
    # Linux Commands
    def ls(args):
        windows_command="dir /b /ogn"
        if not args or args is None:
            # cmdix.runcommandline(windows_command + " ".join(args))
            print(subprocess.check_output(windows_command.split(" "), shell=True, cwd=os.getcwd(), text=True))
            #return subprocess.run(windows_command.split(" "), capture_output=True, text=True, shell=True,cwd=os.path.dirname(os.path.realpath(__file__))).stdout
            #return subprocess.Popen(windows_command.split(" "), stdout=subprocess.PIPE, shell=True, cwd=os.path.dirname(os.path.realpath(__file__))).communicate()[0].decode('utf-8')
            #subprocess.check_output(windows_command.split(" "))
            #subprocess.run(windows_command.split(" "), capture_output=True, shell=True,cwd=os.getcwd()).stdout.decode('utf-8')
            # op = subprocess.Popen(windows_command.split(" "), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            # if op:
            #     o, e = op.communicate()
            #     # print(op.stdout.read())
            #     #print('Error: '  + e.decode('ascii'))
            #     #print('code: ' + str(proc.returncode))
            #     return o.decode('ascii')
        else:
            print(subprocess.check_output(windows_command.split(" ").append(args), shell=True, cwd=os.getcwd(), text=True))
            #return subprocess.run(windows_command.split(" ").append(args), capture_output=True, text=True).stdout
            #return subprocess.Popen(windows_command.split(" ").append(args), stdout=subprocess.PIPE, shell=True, cwd = os.path.dirname(os.path.realpath(__file__))).communicate()[0].decode('utf-8')
            # subprocess.check_output(windows_command.split(" ").append(args))
            #subprocess.run(windows_command.split(" ").append(args), shell=True)
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

    #def pythonusemefix(): #not meant for use, tricks the interpreter to loading these funcs in locals
        #man("_")
        #ls("_")
        #scenegraph("_")
    
    #pythonusemefix()

    def autocomplete(search_word):
        autocomplete = fast_autocomplete.AutoComplete(words=words)
        ac_output = []
        if search_word:
            ac_output = autocomplete.search(word=search_word[0])
        #print(ac_output)
        #return [''.join(x) for x in ac_output]
        return ['_autocomplete'] + ac_output

    def plot(_):
        x, y, z = np.pi*np.mgrid[-1:1:7j, -1:1:7j, -1:1:7j]
        vol = np.cos(x) + np.cos(y) + np.cos(z)
        iso_val=0.0
        verts, faces, normals, values = marching_cubes(vol, iso_val, spacing=(0.4, 0.4, 0.4))
        return ("_vertices", [["X=%.3f"%x[0] + " Y=%.3f"%x[1] + " Z=%.3f"%x[2]]for x in verts] , "_faces", [["X=%s"%x[0] + " Y=%s"%x[1] + " Z=%s"%x[2]]for x in faces] , "_normals", [["X=%.3f"%x[0] + " Y=%.3f"%x[1] + " Z=%.3f"%x[2]]for x in normals])

    

        # def print_result_under_mouse():
        #     print("m1 clicked")
        #     myHandler = CollisionHandlerQueue()
        #     myTraverser = CollisionTraverser('')
        #     pickerNode = CollisionNode('mouseRay')
        #     pickerNP = camera.attachNewNode(pickerNode)
        #     pickerNode.setFromCollideMask(1)
        #     pickerRay = CollisionRay()
        #     pickerNode.addSolid(pickerRay)
        #     myTraverser.addCollider(pickerNP, myHandler)
        #     mpos = base.mouseWatcherNode.getMouse()
        #     pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())

        #     myTraverser.traverse(render)
        #     # Assume for simplicity's sake that myHandler is a CollisionHandlerQueue.
        #     if myHandler.getNumEntries() > 0:
        #         # This is so we get the closest object
        #         myHandler.sortEntries()
        #         pickedObj = myHandler.getEntry(0).getIntoNodePath()
        #         print(pickedObj)
            
        # base.accept('mouse1', print_result_under_mouse)

            # pickerNode = CollisionNode('mouseRay')
            # pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
            # pickerRay = CollisionRay()
            # myTraverser = CollisionTraverser("")
            # myHandler = CollisionHandlerQueue()
            # pickerNode.addSolid(pickerRay)
            # rayNP = base.cam.attachNewNode(pickerNode)
            # myTraverser.addCollider(rayNP, myHandler)
            # if base.mouseWatcherNode.hasMouse():
            #     mpos = base.mouseWatcherNode.getMouse()
            #     pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            #     myTraverser.traverse(render)
            # # Assume for simplicity's sake that myHandler is a CollisionHandlerQueue.
            # # Get the first node path in the sorted queue and discard the rest.
            # if myHandler.getNumEntries() > 0:
            #     myHandler.sortEntries()
            #     print(myHandler.getEntry(0).getIntoNodePath())

        

        # if base.mouseWatcherNode.hasMouse():
        #     # This gives up the screen coordinates of the mouse.
        #     mpos = base.mouseWatcherNode.getMouse()
        #     pickRay(base.camNode, (mpos.x, mpos.y), )

        # # Returns a collision entry for the closest object colliding with the ray.
        # def pickRay(rootNP, origin, dir):
        #     traverser = CollisionTraverser("")
        #     chq = CollisionHandlerQueue()
        #     rayNode = CollisionNode("")
        #     ray = CollisionRay()

        #     # Make a collision node with one collision ray.
        #     ray.setOrigin(origin)
        #     ray.setDirection(dir)
        #     rayNode.addSolid(ray)

        #     # Attach the collision node to the provided node path.
        #     rayNP = rootNP.attachNewNode(rayNode)

        #     # This will let the ray detect collisions with normal geometry.
        #     rayNode.setFromCollideMask(GeomNode.getDefaultCollideMask())

        #     # Add the queue to a traverser, which will do the traversal
        #     # on the provided root node path.
        #     traverser.addCollider(rayNP, chq)
        #     traverser.traverse(rootNP)

        #     # Get the first node path in the sorted queue and discard the rest.
        #     if chq.getNumEntries() < 1:
        #         return None
        #     chq.sortEntries()
        #     return chq.getEntry(0)


MainApp().run()