from p10ga_py import *
import numpy as np
from skimage.measure import marching_cubes

# TODO: psutils rendering after building ndplot

# In absence of order, consider repetition repeats
class FiniteRepetitionSelector:
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
    def __init__(self, current_operator="+", current_operand=2):
        self.operators = ["C/S", "+", "*", "^", "↑", "↑↑"]
        self.current_operator = current_operator
        self.current_operand = current_operand
        self.autonegate_threshold = 0.0
        self.autonegate = False

    def autonegate_value(self, value):
        if self.autonegate:  # can be used to complete circles within engineering-tolerance
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
            return self.basic_tetration(value, self.current_operand)
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


class SpatialDimensionSelector:
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


# See the folder "Nd-Plotting Development" for an example of what final plots look like
def Cartesian4D_to_P10GA(x, y, z, w):
    output = (e_0() + x * e_1() + y * e_2() + z * e_3() + w * e_4()).dual()
    # output = (output | e_2())/ e_2()  # inner product used to take arbitrarily high dimensional point and project it to a lower basis "magic"
    return output


def plot():
    x, y, z = np.pi * np.mgrid[-1:1:7j, -1:1:7j, -1:1:7j]
    vol = np.cos(x) + np.cos(y) + np.cos(z)
    iso_val = 0.0
    verts, faces, normals, values = marching_cubes(vol, iso_val, spacing=(0.4, 0.4, 0.4))  # The marching cubes algorithm is here for education
    return ("_vertices", [["X=%.3f" % x[0] + " Y=%.3f" % x[1] + " Z=%.3f" % x[2]] for x in verts], "_faces",
            [["X=%s" % x[0] + " Y=%s" % x[1] + " Z=%s" % x[2]] for x in faces], "_normals",
            [["X=%.3f" % x[0] + " Y=%.3f" % x[1] + " Z=%.3f" % x[2]] for x in normals])


class Cylinder:
    def __init__(self, line_start, line_end, line_thickness, reparent_to):
        self.line_start = np.array(line_start)
        self.line_end = np.array(line_end)
        self.line_thickness = line_thickness
        self.line_midpoint = (np.array(line_start) + np.array(line_end)) / 2.0
        self.model = loader.loadModel("models/Cylinder.bam")
        self.model.reparent_to(reparent_to)
        euler_angles = look_at_rotation(self.line_midpoint, self.line_end)
        euler_angles = [x + 180 for x in euler_angles]
        self.model.setPosHprScale(self.line_midpoint[0], self.line_midpoint[1], self.line_midpoint[2], euler_angles[2] + 90, euler_angles[1] + 270, euler_angles[0], line_thickness, line_thickness,
                                  float(np.sqrt((self.line_end - self.line_start).dot((self.line_end - self.line_start)))) / 2)

    def update(self, line_start, line_end, line_thickness):
        self.line_start = np.array(line_start)
        self.line_end = np.array(line_end)
        self.line_thickness = line_thickness
        self.line_midpoint = (np.array(line_start) + np.array(line_end)) / 2.0
        euler_angles = look_at_rotation(self.line_midpoint, self.line_end)
        euler_angles = [x + 180 for x in euler_angles]  # [x + 360 if x < 0 else x for x in euler_angles]
        # print(euler_angles)  # roll, pitch, yaw
        self.model.setPosHprScale(self.line_midpoint[0], self.line_midpoint[1], self.line_midpoint[2], euler_angles[2] + 90, euler_angles[1] + 270, euler_angles[0], line_thickness, line_thickness,
                                  float(np.sqrt((self.line_end - self.line_start).dot((self.line_end - self.line_start)))) / 2)


def look_at_rotation(start, target):  # code from a gpt tested to work with input vectors set to zero
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
