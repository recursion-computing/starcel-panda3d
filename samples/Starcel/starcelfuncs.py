import numpy as np
from panda3d.core import *
from direct.interval.IntervalGlobal import *
import uuid

class Cylinder():
    def __init__(self, line_start, line_end, line_thickness, reparent_to):
        self.line_start = np.array(line_start)
        self.line_end = np.array(line_end)
        self.line_thickness = line_thickness
        self.line_midpoint = (np.array(line_start) + np.array(line_end)) / 2.0
        self.model = loader.loadModel("models/Cylinder.bam")
        self.model.reparent_to(reparent_to)
        euler_angles = look_at_rotation(self.line_midpoint, self.line_end)
        euler_angles = [x + 180 for x in euler_angles]
        self.model.setPosHprScale(self.line_midpoint[0], self.line_midpoint[1], self.line_midpoint[2], euler_angles[2]+90, euler_angles[1]+270, euler_angles[0], line_thickness, line_thickness, float(np.sqrt((self.line_end - self.line_start).dot((self.line_end - self.line_start))))/2)

    def update(self, line_start, line_end, line_thickness):
        self.line_start = np.array(line_start)
        self.line_end = np.array(line_end)
        self.line_thickness = line_thickness
        self.line_midpoint = (np.array(line_start) + np.array(line_end)) / 2.0
        euler_angles = look_at_rotation(self.line_midpoint, self.line_end)
        euler_angles = [x + 180 for x in euler_angles]  # [x + 360 if x < 0 else x for x in euler_angles]
        # print(euler_angles)  # roll, pitch, yaw
        self.model.setPosHprScale(self.line_midpoint[0], self.line_midpoint[1], self.line_midpoint[2], euler_angles[2]+90, euler_angles[1]+270, euler_angles[0], line_thickness, line_thickness, float(np.sqrt((self.line_end - self.line_start).dot((self.line_end - self.line_start))))/2)

class SCell():
    def __init__(self, most_recent_owner, text="=", pos=(0, 0, 0)):
        ### Code to spawn 3D Text
        self.focused = False
        self.most_recent_owner = most_recent_owner
        self.font = loader.loadFont("SourceCodePro-Bold.ttf", color=(1, 1, 1, 1), renderMode=TextFont.RMSolid, scaleFactor=23) # .6 1.4
        self.text = TextNode('Text' + str(uuid.uuid4()))
        self.text.setText(text)
        self.text.setFont(self.font)
        self.text.setAlign(TextNode.ALeft)
        self.textNode = render.attachNewNode(self.text)  # text.generate()
        self.textNode.setPos(pos)
        self.textNode.setScale(1, .1, 1)
        # pt1, pt2 = textNode.getTightBounds()
        # width = pt2.getX() - pt1.getX()
        # height = pt2.getY() - pt1.getY()
        # depth = pt2.getZ() - pt1.getZ()
        # print(width) #.6
        # print(height) #.1
        # print(depth) #1.4
        self.textNode.node().setIntoCollideMask(BitMask32.bit(1))
        self.collision_node = CollisionNode('TextColNode')
        self.fromObject = self.textNode.attachNewNode(self.collision_node)
        # fromObject.show()
        self.fromObject.node().addSolid(CollisionBox(self.textNode.getTightBounds()[0] - self.textNode.getPos(),
                                                self.textNode.getTightBounds()[1] - self.textNode.getPos()))

        self.box_extents = [self.textNode.getTightBounds()[0] - self.textNode.getPos(),
                                                self.textNode.getTightBounds()[1] - self.textNode.getPos()]

        self.cursor = Cursor(len(text),len(text),self)

        self.textNode.setHpr(self.most_recent_owner.drone.get_hpr()) # + (180, 0, 0))
        # try:
        #     entry._d_entry.set(textNode.node().text)
        # except:
        #     pass
        # print(len(entry._edited_text))
        # entry._d_entry.guiItem.set_focus(True)
        # entry._d_entry.setCursorPosition(len(entry._edited_text))
        # self.hud_bound_textNode = textNode
        # print(textNode)
        # self.update()


class Cursor():
    def __init__(self, start, end, parent_scell):
        self.parent_scell = parent_scell
        self.model = loader.loadModel("models/cursor4.bam")
        self.model.set_scale(.05,.4,.4) # set x to .5 for full character width
        #self.model.hide()
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
        # self.highlight.set_scale(.5,.4,.4)  # set x to .5 for full character width
        # self.parent_scell.most_recent_owner.render_pipeline.prepare_scene(self.highlight)
        # self.highlight.reparent_to(self.parent_scell.textNode)

    def update(self, start, end):
        self.location_start = start
        self.location_end = end
        pass

    def get_click_coordinates(self, hit_pos):
        self.parent_scell.most_recent_owner.keyboard_capturer.set_active_scell(self.parent_scell)
        # self.parent_scell.fromObject.node().modifySolid((CollisionBox(self.parent_scell.textNode.getTightBounds()[0] - self.parent_scell.textNode.getPos(),
        #                                         self.parent_scell.textNode.getTightBounds()[1] - self.parent_scell.textNode.getPos())))
        # self.box_extents = [self.parent_scell.textNode.getTightBounds()[0] - self.parent_scell.textNode.getPos(),
        #                                         self.parent_scell.textNode.getTightBounds()[1] - self.parent_scell.textNode.getPos()]

        pt1, pt2 = self.parent_scell.box_extents # textNode.getTightBounds()  # cursor.model.right

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
        # print(hit_pos_in_textNode)

        # self.parent_scell.textNode.getPos() + (self.parent_scell.textNode.get_hpr().right * )
        # self.parent_scell.textNode.getPos() + (self.parent_scell.textNode.get_hpr().up * )
        self.click_width = (hit_pos_in_textNode[0] // (box_extents_width / self.max_characters_width))
        self.click_height = (hit_pos_in_textNode[2] // (box_extents_depth / self.max_characters_height + 1))
        # print(box_extents_width)
        # print(box_extents_height)
        # print(box_extents_depth)
        # print(self.max_characters_width)
        # print(self.max_characters_height)
        # print(self.click_width)
        # print(self.click_height)

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


class KeyboardCapturer():
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

def look_at_rotation(start, target):  # tested to work with input vectors set to zero
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

class SpatialDimensionSelector():
    def __init__(self):  # SpherePoints provided by WolframLang
        Line2 = [[-1.000000, 0.000000, 0.000000], [1.000000, 0.000000, 0.000000]]
        Plane4 = [[0.000000, 1.000000, 0.000000], [1.000000, 0.000000, 0.000000], [0.000000, -1.000000, 0.000000],
                  [-1.000000, 0.000000, 0.000000]]
        Optimal6 = [[1.000000, 0.000000, 0.000000], [-1.000000, 0.000000, 0.000000], [0.000000, 1.000000, 0.000000],
                    [0.000000, -1.000000, 0.000000], [0.000000, 0.000000, 1.000000], [0.000000, 0.000000, -1.000000]]
        Optimal4 = [[0.577350, 0.577350, 0.577350], [-0.577350, -0.577350, 0.577350], [-0.577350, 0.577350, -0.577350],
                    [0.577350, -0.577350, -0.577350]]
        SpherePoints5 = [[-1.000000, 0.000000, 0.000000], [1.000000, 0.000000, 0.000000], [0.000000, -0.866025, -0.500000],
                    [0.000000, 0.866025, -0.500000], [0.000000, 0.000000, 1.000000]]
        Optimal6_0 = [[1.000000, 0.000000, 0.000000], [-1.000000, 0.000000, 0.000000], [0.000000, 1.000000, 0.000000],
                      [0.000000, -1.000000, 0.000000], [0.000000, 0.000000, 1.000000], [0.000000, 0.000000, -1.000000]]
        SpherePoints7 = [[0.000000, 0.000000, -1.000000], [0.000000, 0.000000, 1.000000], [1.000000, 0.000000, 0.000000],
                    [0.309017, -0.951057, 0.000000], [0.309017, 0.951057, 0.000000], [-0.809017, -0.587785, 0.000000],
                    [-0.809017, 0.587785, 0.000000]]
        Optimal8 = [[0.859533, 0.000000, 0.511081], [-0.859533, 0.000000, 0.511081], [0.000000, 0.859533, 0.511081],
                    [0.000000, -0.859533, 0.511081], [0.607781, 0.607781, -0.511081], [0.607781, -0.607781, -0.511081],
                    [-0.607781, 0.607781, -0.511081], [-0.607781, -0.607781, -0.511081]]
        Cube8 = [[0.577350, 0.577350, 0.577350], [-0.577350, 0.577350, 0.577350], [0.577350, -0.577350, 0.577350],
                 [-0.577350, -0.577350, 0.577350], [0.577350, 0.577350, -0.577350], [-0.577350, 0.577350, -0.577350],
                 [0.577350, -0.577350, -0.577350], [-0.577350, -0.577350, -0.577350]]
        SpherePoints9 = [[-0.37796447300922725, -0.6546536707079771, -0.6546536707079771],
                    [-0.37796447300922725, -0.6546536707079771, 0.6546536707079771],
                    [-0.37796447300922725, 0.6546536707079771, -0.6546536707079771],
                    [-0.37796447300922725, 0.6546536707079771, 0.6546536707079771],
                    [0.7559289460184545, 0., -0.6546536707079771], [0.7559289460184545, 0., 0.6546536707079771],
                    [-1., 0., 0.], [0.5, -0.8660254037844386, 0.], [0.5, 0.8660254037844386, 0.]]
        SpherePoints10 = [[-0.8944271909999157, 0., -0.44721359549995787], [0.8944271909999157, 0., 0.44721359549995787],
                     [-0.7236067977499789, -0.5257311121191336, 0.44721359549995787],
                     [-0.7236067977499789, 0.5257311121191336, 0.44721359549995787],
                     [-0.276393202250021, -0.85065080835204, -0.44721359549995787],
                     [-0.276393202250021, 0.85065080835204, -0.44721359549995787],
                     [0.276393202250021, -0.85065080835204, 0.44721359549995787],
                     [0.276393202250021, 0.85065080835204, 0.44721359549995787],
                     [0.7236067977499789, -0.5257311121191336, -0.44721359549995787],
                     [0.7236067977499789, 0.5257311121191336, -0.44721359549995787]]
        SpherePoints11 = [[0., 0., 1.], [-0.8944271909999157, 0., -0.44721359549995787],
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