import numpy as np
from panda3d.core import *
from direct.interval.IntervalGlobal import *
import uuid
import sys

class SCell:
    def __init__(self, most_recent_owner, text="=", pos=(0, 0, 0)):
        # Editable and Submittable 3D Text
        self.focused = False
        self.most_recent_owner = most_recent_owner
        self.most_recent_owner.stdout_handler = StdoutHandler()
        self.most_recent_owner.stdout_handler.start()
        self.font = loader.loadFont("SourceCodePro-Bold.ttf", color=(1, 1, 1, 1), renderMode=TextFont.RMSolid, scaleFactor=23) # .6 1.4
        self.text = TextNode('Text' + str(uuid.uuid4()))
        self.text.setText(text)
        self.text.setFont(self.font)
        self.text.setAlign(TextNode.ALeft)
        self.textNode = render.attachNewNode(self.text)  # text.generate()
        self.textNode.setPos(pos)
        self.textNode.setScale(1, .1, 1)
        self.textNode.node().setIntoCollideMask(BitMask32.bit(1))
        self.collision_node = CollisionNode('TextColNode')
        self.fromObject = self.textNode.attachNewNode(self.collision_node)
        # fromObject.show()
        self.fromObject.node().addSolid(CollisionBox(self.textNode.getTightBounds()[0] - self.textNode.getPos(),
                                                self.textNode.getTightBounds()[1] - self.textNode.getPos()))

        self.box_extents = [self.textNode.getTightBounds()[0] - self.textNode.getPos(),
                                                self.textNode.getTightBounds()[1] - self.textNode.getPos()]

        self.textNode.setHpr(self.most_recent_owner.drone.get_hpr())

        self.cursor = Cursor(len(text),len(text),self)

class Cursor:
    def __init__(self, start, end, parent_scell):
        self.parent_scell = parent_scell
        self.model = loader.loadModel("models/cursor4.bam")
        self.model.set_scale(.05,.4,.4) # set x to .5 for full character width
        # self.model.hide()
        self.model.reparent_to(parent_scell.textNode)
        self.location_start = 0
        self.location_end = None
        self.cursor_shown = False
        self.cursor_seq = Sequence()
        self.cursor_seq.append(Func(lambda: self.model.show() if self.cursor_shown else None))
        self.cursor_seq.append(Wait(.3))
        self.cursor_seq.append(Func(lambda: self.model.hide()))
        self.cursor_seq.append(Wait(.3))
        self.cursor_seq.loop()
        # self.spawn_corner_markers(self.parent_scell.textNode.getTightBounds()[0],self.parent_scell.textNode.getTightBounds()[1])
        self.max_characters_width = 1
        self.max_characters_height = 1
        self.click_width = None
        self.click_height = None
        # self.highlight = loader.loadModel("models/cursor2.glb") # TODO: Unsure how to import transparent models
        # self.highlight.setTransparency(TransparencyAttrib.MAlpha)
        # self.highlight.setAlphaScale(0.5)
        # self.highlight.set_scale(.5,.4,.4)  # set x to .5 for full character width
        # self.parent_scell.most_recent_owner.render_pipeline.prepare_scene(self.highlight)
        # self.highlight.reparent_to(self.parent_scell.textNode)

    def update(self, start, end):
        self.location_start = start
        self.location_end = end
        pass

    def get_click_coordinates(self, hit_pos):
        self.parent_scell.most_recent_owner.keyboard_capturer.set_active_scell(self.parent_scell)
        pt1, pt2 = self.parent_scell.box_extents  # textNode.getTightBounds()  # cursor.model.right

        box_extents_width = pt2.getX() - pt1.getX()
        box_extents_height = pt2.getY() - pt1.getY()
        box_extents_depth = pt2.getZ() - pt1.getZ()

        model3 = loader.loadModel("models/coordinate2.bam")  # y and z are flipped
        model3.reparent_to(render)
        model3.setScale(.5)
        model3.setHpr(self.parent_scell.textNode.get_hpr())
        model3.setPos(hit_pos)
        model3.hide()

        textNode_text = self.parent_scell.text.getText()

        self.max_characters_width = len(textNode_text.split("\n")[0])
        self.max_characters_height = len(textNode_text.split("\n"))

        hit_pos_in_textNode = self.parent_scell.textNode.get_relative_point(render, hit_pos)

        self.click_width = (hit_pos_in_textNode[0] // (box_extents_width / self.max_characters_width))
        self.click_height = (hit_pos_in_textNode[2] // (box_extents_depth / self.max_characters_height + 1))

        self.model.set_pos(self.click_width * .6, 0, self.click_height * 1.2)

        self.parent_scell.most_recent_owner.keyboard_capturer.clear_buffer()


    def spawn_corner_markers(self, pt1, pt2):
        model2 = loader.loadModel("models/coordinate2.bam")  # y and z are flipped
        model2.reparent_to(self.parent_scell.textNode)
        model2.setScale(.25)
        model2.setPos(pt1 - self.parent_scell.textNode.getPos())  # self.parent_scell.textNode.getRelativePoint(render, pt1))
        model2.setHpr(self.parent_scell.textNode.get_hpr())

        model4 = loader.loadModel("models/coordinate2.bam")  # y and z are flipped
        model4.reparent_to(self.parent_scell.textNode)
        model4.setScale(.25)
        model4.setPos(pt2 - self.parent_scell.textNode.getPos())  # self.parent_scell.textNode.getRelativePoint(render, pt2))
        model4.setHpr(self.parent_scell.textNode.get_hpr())


class KeyboardCapturer:
    def __init__(self):
        base.buttonThrowers[0].node().setKeystrokeEvent('keystroke')
        base.accept('keystroke', self.myFunc)
        self.buffer = ""
        self.active_scell = None
    def myFunc(self, keyname):
        self.buffer += keyname
        if self.active_scell is not None:
            insert_index = int((-self.active_scell.cursor.click_height * self.active_scell.cursor.max_characters_width) + self.active_scell.cursor.click_width) + 1
            self.active_scell.text.setText(self.active_scell.text.getText()[:insert_index] + keyname + self.active_scell.text.getText()[insert_index:])
            self.active_scell.cursor.click_width += 1
            self.active_scell.cursor.model.set_pos(self.active_scell.cursor.click_width * .6, 0, self.active_scell.cursor.click_height * 1.2)
        # print(keyname)
        # print(self.buffer)

    def set_active_scell(self, scell):
        self.active_scell = scell

    def clear_buffer(self):
        self.buffer = ""



class StdoutHandler:  # Used to capture stdout data printed to console
    def __init__(self):
        self.last_output = ""

    def start(self):
        self._handled_stdout = sys.stdout
        sys.stdout = self

    def write(self, data: str):
        # write(data="") is called for the end kwarg in print(..., end="")
        if data:
            self.last_output += data
            self._handled_stdout.write(data)

    def end(self):
        sys.stdout = self._handled_stdout

    def flush(self):
        self._handled_stdout.flush()