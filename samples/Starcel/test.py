import numpy as np
import math

# def look_at_rotation(v1, v2):
#     # Translating vectors away from the origin
#     translation_v1 = np.array([1.0, 0.0, 0.0]) if np.linalg.norm(v1) < 1e-6 else np.zeros(3)
#     translation_v2 = np.array([1.0, 0.0, 0.0]) if np.linalg.norm(v2) < 1e-6 else np.zeros(3)
#
#     v1_translated = v1 + translation_v1
#     v2_translated = v2 + translation_v2
#
#     # Normalize translated input vectors
#     norm_v1 = np.linalg.norm(v1_translated)
#     norm_v2 = np.linalg.norm(v2_translated)
#
#     v1_normalized = v1_translated / norm_v1
#     v2_normalized = v2_translated / norm_v2
#
#     # Calculate the axis of rotation
#     axis = np.cross(v1_normalized, v2_normalized)
#     axis /= np.linalg.norm(axis)
#
#     # Calculate the angle of rotation (in radians)
#     angle = np.arccos(np.dot(v1_normalized, v2_normalized))
#
#     # Check for a small angle to avoid divide by zero in quaternion calculation
#     epsilon = 1e-10
#     if np.abs(angle) < epsilon:
#         return np.array([1.0, 0.0, 0.0, 0.0])  # No rotation for small angles
#
#     # Convert axis-angle representation to quaternion
#     quaternion = np.array([np.cos(angle/2), *axis * np.sin(angle/2)])
#
#     return quaternion_to_euler(quaternion)
#
#
# def quaternion_to_euler(quaternion):
#     w, x, y, z = quaternion
#
#     t0 = +2.0 * (w * x + y * z)
#     t1 = +1.0 - 2.0 * (x * x + y * y)
#     roll_x = np.arctan2(t0, t1)
#
#     t2 = +2.0 * (w * y - z * x)
#     t2 = +1.0 if t2 > +1.0 else t2
#     t2 = -1.0 if t2 < -1.0 else t2
#     pitch_y = np.arcsin(t2)
#
#     t3 = +2.0 * (w * z + x * y)
#     t4 = +1.0 - 2.0 * (y * y + z * z)
#     yaw_z = np.arctan2(t3, t4)
#
#     return yaw_z * 360, pitch_y * 360, roll_x * 360
#



# def LookAt(target, current, eye, up):
#     # turn vectors into unit vectors
#     n1 = (current - eye) / abs(current - eye)
#     n2 = (target - eye) / abs(target - eye)
#     d = n1.x * n2.x + n1.y * n2.y + n1.z * n2.z
#
#     # if no noticeable rotation is available, return zero rotation
#     # this way we avoid Cross product artifacts
#     if d > 0.9998:
#         return (0, 0, 1, 0)
#
#     # in this case, there are 2 lines on the same axis
#     if d < -0.9998:
#         angle = 0.5
#         n1 = [n1.x, n1.y * math.cos(angle) - n1.z * math.sin(angle), n1.y * math.sin(angle) + n1.z * math.cos(angle)]
#
#     axis = [n1[1] * n2[2] - n1[2] * n2[1], n1[2] * n2[0] - n1[0] * n2[2], n1[0] * n2[1] - n1[1] * n2[0]]
#     pointToTarget = (1.0 + d, axis[0], axis[1], axis[2])
#
#     length = math.sqrt(pointToTarget[0]**2 + pointToTarget[1]**2 + pointToTarget[2]**2 + pointToTarget[3]**2)
#     pointToTarget = (pointToTarget[0] / length, pointToTarget[1] / length, pointToTarget[2] / length, pointToTarget[3] / length)
#
#     # now twist around the target vector, so that the 'up' vector points along the z-axis
#     a = pointToTarget[0]
#     b = pointToTarget[1]
#     c = pointToTarget[2]
#     upProjected = (b * b + c * c, -a * b, -a * c)
#     yaxisProjected = (-b * a, a * a + c * c, -b * c)
#
#     d = upProjected[0] * yaxisProjected[0] + upProjected[1] * yaxisProjected[1] + upProjected[2] * yaxisProjected[2]
#
#     # so the axis of twist is n2, and the angle is arccos(d)
#     # convert this to quat as follows
#     s = math.sqrt(1.0 - d * d)
#     twist = (d, n2[0] * s, n2[1] * s, n2[2] * s)
#
#     return (pointToTarget[0] * twist[0] - pointToTarget[1] * twist[1] - pointToTarget[2] * twist[2] - pointToTarget[3] * twist[3],
#             pointToTarget[0] * twist[1] + pointToTarget[1] * twist[0] + pointToTarget[2] * twist[3] - pointToTarget[3] * twist[2],
#             pointToTarget[0] * twist[2] - pointToTarget[1] * twist[3] + pointToTarget[2] * twist[0] + pointToTarget[3] * twist[1],
#             pointToTarget[0] * twist[3] + pointToTarget[1] * twist[2] - pointToTarget[2] * twist[1] + pointToTarget[3] * twist[0])
#


import numpy as np

# def rotate_to_360_degrees(start, target):
#     # Check if both start and target vectors are zero
#     start_is_zero = np.allclose(start, [0, 0, 0])
#     target_is_zero = np.allclose(target, [0, 0, 0])
#
#     # Add an offset to both start and target vectors if they are zero
#     if start_is_zero and target_is_zero:
#         start_offset = np.array([1, 1, 1])
#         target_offset = np.array([1, 1, 1])
#     else:
#         start_offset = np.array([0, 0, 0])
#         target_offset = np.array([0, 0, 0])
#
#     start = np.array(start) + start_offset
#     target = np.array(target) + target_offset
#
#     try:
#         # Calculate the rotation matrix
#         rotation_matrix = np.dot(np.linalg.inv(np.diag(start)), np.diag(target))
#     except np.linalg.LinAlgError as e:
#         # Handle the LinAlgError (Singular matrix) by printing a message
#         print(f"Error: {e}")
#         return None  # or any other appropriate action
#
#     # Extract rotation angles around each axis
#     # The returned angles are in radians, so we convert them to degrees
#     angles = np.degrees(np.arcsin(rotation_matrix))
#
#     return tuple(angles)
#
# # Sample input and output
# start_vector = [0, 0, 0]
# target_vector = [100, 100, 100]
#
# rotation_angles = rotate_to_360_degrees(start_vector, target_vector)
# print(rotation_angles)

def look_at_rotation(start, target):
    # Check if both start and target vectors are zero
    start_is_zero = np.allclose(start, [0.0, 0.0, 0.0])
    target_is_zero = np.allclose(target, [0.0, 0.0, 0.0])

    # Add an offset to both start and target vectors if they are zero
    if start_is_zero and target_is_zero:
        start += np.array([1.0, 1.0, 1.0])
        target += np.array([1.0, 1.0, 1.0])

    # Calculate the forward direction and up direction
    forward = (target - start) / np.linalg.norm(target - start)
    up = np.array([0.0, 1.0, 0.0])  # Assuming the up direction is the positive Y-axis

    # Calculate the right direction using cross product
    right = np.cross(up, forward) / np.linalg.norm(np.cross(up, forward))

    # Calculate the up direction using cross product again
    new_up = np.cross(forward, right) / np.linalg.norm(np.cross(forward, right))

    # Build the rotation matrix
    rotation_matrix = np.column_stack((right, new_up, -forward))

    # Convert the rotation matrix to Euler angles
    euler_angles = (np.degrees(np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])),
                   np.degrees(np.arctan2(-rotation_matrix[2, 0], np.sqrt(rotation_matrix[2, 1]**2 + rotation_matrix[2, 2]**2))),
                   np.degrees(np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])))
    return tuple(euler_angles)

# Sample input and output
start_vector = np.array([0.0, 0.0, 0.0])
target_vector = np.array([100.0, 100.0, 100.0])

rotation_angles = look_at_rotation(start_vector, target_vector)
print("Rotation Angles:", rotation_angles)

# Wolfram13 = [[-0.4424213268469919, 0.405294176556914, -0.8],
#              [0.06516328781643593, -0.7425020548634917, -0.6666666666666667],
#              [0.5146815777435377, 0.6713109779282461, -0.5333333333333333],
#              [-0.9025048168603472, -0.15964039446164913, -0.4],
#              [0.8132019196635456, -0.5172924963155886, -0.2666666666666667],
#              [-0.2572863629176943, 0.9570924457328073, -0.1333333333333333],
#              [-0.4609070247133692, -0.8874484292452546, 0.],
#              [0.9309343311316439, 0.3399757246373645, 0.1333333333333333],
#              [-0.8908739125019206, 0.3677398005552421, 0.2666666666666666],
#              [0.38846127106218875, -0.8301191727003713, 0.3999999999999999],
#              [0.25316576804094076, 0.8071323617894381, 0.5333333333333332],
#              [-0.644890359967681, -0.37372714535648904, 0.6666666666666667],
#              [0.5860054641769065, -0.1288316574247505, 0.8]]
# Wolfram14 = [[-1., 0., 0.], [-0.5773502691896258, -0.5773502691896258, -0.5773502691896258],
#              [-0.5773502691896258, -0.5773502691896258, 0.5773502691896258],
#              [-0.5773502691896258, 0.5773502691896258, -0.5773502691896258],
#              [-0.5773502691896258, 0.5773502691896258, 0.5773502691896258], [0., -1., 0.], [0., 0., -1.],
#              [0., 0., 1.], [0., 1., 0.], [0.5773502691896258, -0.5773502691896258, -0.5773502691896258],
#              [0.5773502691896258, -0.5773502691896258, 0.5773502691896258],
#              [0.5773502691896258, 0.5773502691896258, -0.5773502691896258],
#              [0.5773502691896258, 0.5773502691896258, 0.5773502691896258], [1., 0., 0.]]
# Wolfram15 = [[-0.41828987895367725, 0.38318779354697036, -0.8235294117647058],
#              [0.061926184282278966, -0.7056169297192817, -0.7058823529411764],
#              [0.4920383181508844, 0.6417768554767104, -0.5882352941176471],
#              [-0.8688648399842015, -0.1536899562170412, -0.47058823529411764],
#              [0.7894558556407076, -0.5021871941280017, -0.3529411764705882],
#              [-0.25231571005131853, 0.9386018648298068, -0.23529411764705888],
#              [-0.4577062427615897, -0.8812855183691842, -0.11764705882352944],
#              [0.9393212963241169, 0.34303863087410535, 0.],
#              [-0.91792641211384, 0.3789066791361507, 0.11764705882352944],
#              [0.41194618569018737, -0.8803050711520397, 0.23529411764705888],
#              [0.28002360487386924, 0.8927593778084889, 0.3529411764705883],
#              [-0.7634216556646115, -0.4424184540286171, 0.47058823529411753],
#              [0.7898277638965904, -0.17364141825162907, 0.588235294117647],
#              [-0.4073809068254702, 0.5794574191088471, 0.7058823529411764],
#              [-0.07290071832210133, -0.5625698118692463, 0.8235294117647058]]
# Optimal20 = [[0.000000, 0.356822, 0.934172], [0.000000, -0.356822, -0.934172], [0.000000, 0.356822, -0.934172],
#              [0.000000, -0.356822, 0.934172], [0.934172, 0.000000, 0.356822], [-0.934172, 0.000000, -0.356822],
#              [-0.934172, 0.000000, 0.356822], [0.934172, 0.000000, -0.356822], [0.356822, 0.934172, 0.000000],
#              [-0.356822, -0.934172, 0.000000], [0.356822, -0.934172, 0.000000], [-0.356822, 0.934172, 0.000000],
#              [0.577350, 0.577350, 0.577350], [-0.577350, -0.577350, -0.577350], [0.577350, 0.577350, -0.577350],
#              [-0.577350, -0.577350, 0.577350], [0.577350, -0.577350, 0.577350],
#              [-0.577350, 0.577350, -0.577350], [0.577350, -0.577350, -0.577350],
#              [-0.577350, 0.577350, 0.577350]]