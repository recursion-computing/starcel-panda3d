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


quaternions = [[-0.5623345, 0.1889373, -0.1504156, -0.7908598],
[-0.5622921, 0.1888551, -0.1504697, -0.7908992],
[-0.5624943, 0.188538, -0.150771, -0.7907737],
[-0.5636129, 0.1877892, -0.1514927, -0.7900171],
[-0.5652487, 0.1867807, -0.1521715, -0.7889562],
[-0.5672842, 0.1854723, -0.1529503, -0.7876521],
[-0.5696763, 0.1839643, -0.1538157, -0.7861091],
[-0.5725469, 0.1825381, -0.1547642, -0.7841678],
[-0.5760461, 0.1817503, -0.1557752, -0.7815837],
[-0.5813124, 0.1819452, -0.1571724, -0.777348],
[-0.5867311, 0.1830248, -0.158405, -0.7727597],
[-0.5927082, 0.1846297, -0.1598109, -0.7675095],
[-0.6008407, 0.1866296, -0.1622104, -0.7601637],
[-0.6093241, 0.1883039, -0.1658139, -0.7521785],
[-0.6201103, 0.1898345, -0.1710172, -0.7417414],
[-0.6361292, 0.1910775, -0.1792368, -0.7257439],
[-0.6498341, 0.1911684, -0.1864777, -0.711616],
[-0.6713854, 0.1895149, -0.1975706, -0.6886892],
[-0.6898502, 0.1870013, -0.2068575, -0.6680933],
[-0.7062655, 0.1838009, -0.215271, -0.6488959],
[-0.721193, 0.1798161, -0.2230805, -0.6307006],
[-0.7283513, 0.1773656, -0.2274875, -0.6215276],
[-0.7341532, 0.1750629, -0.2320779, -0.6136066],
[-0.7365679, 0.1742497, -0.2351386, -0.6097672],
[-0.7380216, 0.1743583, -0.237755, -0.6069577],
[-0.7396778, 0.1747969, -0.2399285, -0.6039529],
[-0.7425053, 0.1751039, -0.2419098, -0.5995882],
[-0.7461614, 0.1749124, -0.2436254, -0.5943882],
[-0.7507012, 0.1731652, -0.2456535, -0.5883178],
[-0.7560757, 0.1702135, -0.2479587, -0.5812877],
[-0.7639711, 0.1659535, -0.2510353, -0.5707814],
[-0.7719402, 0.162658, -0.2538572, -0.5596512],
[-0.782212, 0.1595287, -0.2574447, -0.544444],
[-0.7899354, 0.1576812, -0.2598398, -0.5325635],
[-0.8004184, 0.1562453, -0.2622884, -0.5158722],
[-0.8087234, 0.1560466, -0.2633281, -0.5022709],
[-0.8163432, 0.1565107, -0.2633465, -0.4896313],
[-0.8241506, 0.1569272, -0.2623516, -0.4767843],
[-0.8303959, 0.1567274, -0.2604051, -0.46698],
[-0.8364745, 0.1562313, -0.2578047, -0.4576472],
[-0.8427711, 0.1549948, -0.2546635, -0.4481765],
[-0.8509021, 0.1521894, -0.2502896, -0.4360748],
[-0.8581957, 0.1494553, -0.2467027, -0.4246212],
[-0.8655345, 0.1474638, -0.2435506, -0.412055],
[-0.8742067, 0.1457717, -0.2400715, -0.3960817],
[-0.8821536, 0.1440772, -0.2365391, -0.3809165],
[-0.890768, 0.1414195, -0.2323049, -0.3640996],
[-0.9017172, 0.1362414, -0.225828, -0.3425596],
[-0.9095691, 0.13134, -0.220991, -0.3264934],
[-0.9199674, 0.1234155, -0.2152062, -0.3035066],
[-0.9301514, 0.1141739, -0.2104408, -0.2783857],
[-0.9374701, 0.1068075, -0.2070595, -0.2585914],
[-0.9459175, 0.09794879, -0.2035059, -0.2328791],
[-0.9546149, 0.08896072, -0.2007766, -0.2012123],
[-0.9607909, 0.08216113, -0.1994884, -0.1741723],
[-0.9665947, 0.07389955, -0.1984375, -0.1444197],
[-0.9698861, 0.06704924, -0.1980373, -0.1249298],
[-0.9735016, 0.05596244, -0.1979032, -0.09999134],
[-0.975713, 0.04574276, -0.1981384, -0.08144881],
[-0.9770644, 0.03541055, -0.1987807, -0.06766447],
[-0.9780819, 0.02259475, -0.1995136, -0.05513806],
[-0.9786903, 0.01033865, -0.2005871, -0.04270674],
[-0.9790229, -0.005418235, -0.2017363, -0.02807362],
[-0.9788375, -0.01654936, -0.2031964, -0.01776686],
[-0.978304, -0.0300066, -0.2049592, -0.003713119],
[-0.9777721, -0.03920751, -0.2058557, 0.007006731],
[-0.9774478, -0.04679196, -0.2052207, 0.0170877],
[-0.9774006, -0.05377274, -0.2026264, 0.02721123],
[-0.9775188, -0.06065255, -0.1983015, 0.038161],
[-0.977581, -0.06805471, -0.1922049, 0.05256172],
[-0.9774235, -0.07325681, -0.1867838, 0.06625462],
[-0.9768136, -0.07763386, -0.1811662, 0.08359183],
[-0.975872, -0.08016558, -0.1768451, 0.09986981],
[-0.9743386, -0.08273574, -0.1729018, 0.1180033],
[-0.9716207, -0.08696466, -0.1691089, 0.1406875],
[-0.969143, -0.09057187, -0.1667667, 0.1573144],
[-0.9649684, -0.09539358, -0.1638502, 0.1813534],
[-0.9606858, -0.09906481, -0.1609102, 0.2034128],
[-0.9552303, -0.1023732, -0.1580278, 0.2282147],
[-0.9474204, -0.1060312, -0.1557666, 0.2586278],
[-0.9417912, -0.1068853, -0.1549295, 0.2785708],
[-0.9347256, -0.1032833, -0.152931, 0.3036987],
[-0.9307126, -0.09452615, -0.148667, 0.320527],
[-0.9285673, -0.08136313, -0.1428254, 0.3327825],
[-0.9266502, -0.06334978, -0.1364324, 0.3445185],
[-0.9245676, -0.04835187, -0.1317925, 0.3542151],
[-0.9214348, -0.03520792, -0.129284, 0.364698],
[-0.9172724, -0.0226951, -0.1277187, 0.3765433],
[-0.9133028, -0.0139832, -0.1276948, 0.3864938],
[-0.9095606, -0.007653436, -0.1291561, 0.3949181],
[-0.9058337, -0.001549044, -0.133081, 0.4021856],
[-0.9037523, 0.002413287, -0.1368039, 0.4056003],
[-0.9015074, 0.006506302, -0.1418953, 0.4087889],
[-0.8994309, 0.008047806, -0.1463161, 0.4117665],
[-0.8967071, 0.006663348, -0.1509298, 0.4160445],
[-0.8925117, 0.003183718, -0.1559036, 0.4232112],
[-0.8874835, -0.001857755, -0.1598301, 0.4322326],
[-0.8792927, -0.010726, -0.1626364, 0.4475262],
[-0.8725107, -0.01858612, -0.1635467, 0.4600356],
[-0.8653482, -0.02713806, -0.1631691, 0.4730885],
[-0.8579883, -0.03611719, -0.1619843, 0.4861206],
[-0.8502679, -0.04504295, -0.1592145, 0.4996668],
[-0.8429366, -0.0531354, -0.1545371, 0.5125948],
[-0.8377579, -0.05881345, -0.1481821, 0.5222502],
[-0.8344079, -0.06240074, -0.1394855, 0.5295412],
[-0.8341525, -0.0638883, -0.1311309, 0.5318958],
[-0.8353933, -0.06392361, -0.1220789, 0.5320985],
[-0.8374861, -0.06312141, -0.1118627, 0.5311493],
[-0.8397823, -0.06294305, -0.1020258, 0.5295233],
[-0.8417178, -0.0653905, -0.09034194, 0.5282747],
[-0.8421824, -0.06934445, -0.08445989, 0.5280028],
[-0.8415061, -0.07698608, -0.07836176, 0.5289617],
[-0.8400403, -0.08351916, -0.07558104, 0.5307022],
[-0.8368843, -0.0929598, -0.07352653, 0.5343942],
[-0.8333759, -0.1005611, -0.07223376, 0.5386597],
[-0.8289095, -0.1079486, -0.07068468, 0.5442975],
[-0.823029, -0.1164303, -0.06919444, 0.5516152],
[-0.8147827, -0.128166, -0.06874085, 0.5612282],
[-0.8071654, -0.1387658, -0.06955783, 0.5695522],
[-0.7990117, -0.1485373, -0.07103825, 0.578334],
[-0.7906981, -0.1560636, -0.07245269, 0.5875297],
[-0.7814317, -0.1601177, -0.0747377, 0.5984487],
[-0.7741187, -0.159756, -0.07716084, 0.6076709],
[-0.7675144, -0.1565593, -0.07958229, 0.6165038],
[-0.7618678, -0.151922, -0.08182152, 0.6243252],
[-0.7570997, -0.1472698, -0.08390926, 0.6309283],
[-0.7527139, -0.1435681, -0.08652648, 0.6366498],
[-0.7472763, -0.1410002, -0.09018838, 0.6430888],
[-0.7421216, -0.1415078, -0.09345512, 0.6484575],
[-0.7367262, -0.145886, -0.09633767, 0.6532004],
[-0.7301225, -0.1542487, -0.09937932, 0.6582189],
[-0.7243035, -0.1630079, -0.1019687, 0.6621293],
[-0.717444, -0.1732574, -0.1047013, 0.6665535],
[-0.7123151, -0.1817143, -0.1067678, 0.6694681],
[-0.7074337, -0.1896958, -0.1082371, 0.6721888],
[-0.702606, -0.1975752, -0.1087397, 0.6748959],
[-0.6975883, -0.2052213, -0.1085788, 0.6778389],
[-0.6918191, -0.2135084, -0.1078069, 0.6813061],
[-0.6869276, -0.2199599, -0.106768, 0.6843601],
[-0.6819351, -0.2259604, -0.1055754, 0.6875753],
[-0.6767114, -0.231867, -0.1041602, 0.6909771],
[-0.6699294, -0.2395125, -0.1017203, 0.6953276],
[-0.6616657, -0.2484906, -0.0975258, 0.7006705],
[-0.655, -0.2549648, -0.09299248, 0.705209],
[-0.6467547, -0.260532, -0.08531313, 0.7117254],
[-0.6373817, -0.2639937, -0.07439882, 0.720081],
[-0.6289108, -0.2667802, -0.06496757, 0.7273778],
[-0.6199144, -0.2697205, -0.05639222, 0.734695],
[-0.6098861, -0.2723295, -0.04856395, 0.742642],
[-0.5985022, -0.2746296, -0.04190876, 0.7514104],
[-0.582791, -0.277601, -0.03646236, 0.7628652],
[-0.5666562, -0.2808673, -0.0333635, 0.7738871],
[-0.5452766, -0.2864722, -0.03183762, 0.7871429],
[-0.5285754, -0.2911624, -0.03216678, 0.7967423],
[-0.5070884, -0.2970659, -0.03338209, 0.8083929],
[-0.4796189, -0.3036971, -0.03467725, 0.8225154],
[-0.4544075, -0.3087505, -0.03543535, 0.8348241],
[-0.4180158, -0.3144633, -0.03653674, 0.8514934],
[-0.3935063, -0.3180059, -0.0373069, 0.8617619],
[-0.3635393, -0.3220761, -0.03764008, 0.8733211],
[-0.3337678, -0.3253844, -0.03706344, 0.8839404],
[-0.304588, -0.327552, -0.03559626, 0.8936827],
[-0.2700306, -0.3293036, -0.03295109, 0.9041885],
[-0.2395717, -0.330588, -0.03050336, 0.9123522],
[-0.2089384, -0.3319605, -0.02856429, 0.9194189],
[-0.1792802, -0.3336168, -0.02678836, 0.9251167],
[-0.1455133, -0.3357758, -0.02506727, 0.9302968],
[-0.1171438, -0.3372635, -0.02462728, 0.9337687],
[-0.0895533, -0.3374725, -0.02481082, 0.9367374],
[-0.05901334, -0.336702, -0.02519345, 0.9394224],
[-0.03412918, -0.335808, -0.0252096, 0.9409744],
[-0.009553927, -0.3350202, -0.02421712, 0.9418513],
[0.01564792, -0.3340184, -0.02127745, 0.9421965],
[0.04600137, -0.3327796, -0.01490416, 0.9417644],
[0.07245862, -0.3318437, -0.007574237, 0.9405171],
[0.09899653, -0.3315692, 0.0002939553, 0.9382227],
[0.1256205, -0.3321316, 0.007431047, 0.9348012],
[0.1564315, -0.3332587, 0.01421913, 0.9296591],
[0.1816967, -0.3336203, 0.01923477, 0.9248319],
[0.2050882, -0.3328859, 0.02425368, 0.9200747],
[0.2265265, -0.3311168, 0.0294048, 0.9155231],
[0.2466076, -0.3285336, 0.0349139, 0.9110604],
[0.2692011, -0.3248746, 0.04249589, 0.9056383],
[0.2888687, -0.3215429, 0.05014439, 0.900361],
[0.3123907, -0.3177426, 0.05962322, 0.8932503],
[0.3327337, -0.3150054, 0.06701592, 0.8863227],
[0.3522796, -0.3130179, 0.0731343, 0.8789591],
[0.3726086, -0.3111762, 0.07922773, 0.870663],
[0.3853225, -0.3095085, 0.08299768, 0.8653561],
[0.4012402, -0.306039, 0.0878222, 0.8588554],
[0.4136789, -0.3026931, 0.09149317, 0.8537414],
[0.4254082, -0.299564, 0.09458838, 0.848729],
[0.4362252, -0.2966872, 0.09727043, 0.8439322],
[0.4473995, -0.2934019, 0.09996834, 0.8389004],
[0.4557019, -0.2905402, 0.1021574, 0.8351556],
[0.464298, -0.2870591, 0.1048665, 0.8312801],
[0.4701541, -0.2845419, 0.1070401, 0.8285723],
[0.4788325, -0.2811433, 0.1105157, 0.8242952],
[0.4866711, -0.2794152, 0.113499, 0.8198748],
[0.4953887, -0.2778363, 0.1168678, 0.8147008],
[0.5049239, -0.2753904, 0.1206231, 0.809111],
[0.516888, -0.2713742, 0.1255297, 0.8021369],
[0.5277253, -0.2677612, 0.1305074, 0.7954721],
[0.539396, -0.2636327, 0.136113, 0.7880492],
[0.5520273, -0.2589903, 0.1418386, 0.7797887],
[0.567525, -0.2539277, 0.1483734, 0.7690386],
[0.5808133, -0.2502002, 0.1534234, 0.7592863],
[0.593384, -0.2465019, 0.158061, 0.749765],
[0.6068418, -0.2420062, 0.1631459, 0.7392958],
[0.6174949, -0.2382521, 0.1671645, 0.7307467],
[0.6277452, -0.2347706, 0.1704511, 0.7223322],
[0.6392311, -0.2310949, 0.173547, 0.712642],
[0.6469561, -0.2285886, 0.1755049, 0.7059684],
[0.65705, -0.2250091, 0.1780355, 0.6971069],
[0.6647184, -0.2221019, 0.1803165, 0.6901482],
[0.6716026, -0.2196325, 0.1824585, 0.6836805],
[0.6780056, -0.2177975, 0.1840081, 0.6775043],
[0.68476, -0.2163469, 0.1850892, 0.6708491],
[0.6900759, -0.2156378, 0.1860968, 0.6653285],
[0.6931352, -0.2157013, 0.1876273, 0.6616881],
[0.6946672, -0.2162085, 0.1891298, 0.6594847],
[0.6954437, -0.2167655, 0.1910772, 0.6579202],
[0.6945469, -0.2169877, 0.1932216, 0.6581675],
[0.6932938, -0.2171832, 0.1941515, 0.6591498],
[0.6912625, -0.2183787, 0.193884, 0.6609644],
[0.6893485, -0.2202293, 0.1921096, 0.6628648],
[0.6876652, -0.2219557, 0.189739, 0.6647177],
[0.6852441, -0.2236796, 0.1866252, 0.6675158],
[0.6820774, -0.2246594, 0.184061, 0.6711326],
[0.6778055, -0.2255048, 0.1823426, 0.6756312],
[0.6728993, -0.2271242, 0.18103, 0.6803295],
[0.6685264, -0.2293595, 0.1798126, 0.6842027],
[0.6638981, -0.2323035, 0.1787573, 0.6879819],
[0.6589888, -0.2356866, 0.17824, 0.6916755],
[0.6528224, -0.2397564, 0.1786341, 0.696009],
[0.6472433, -0.2429885, 0.1798203, 0.6997839],
[0.6412643, -0.2458676, 0.1814304, 0.7038557],
[0.6374059, -0.2471572, 0.1826993, 0.7065752],
[0.6344453, -0.2487017, 0.1844675, 0.7082364],
[0.632528, -0.2500199, 0.1867453, 0.7088901],
[0.6325095, -0.251027, 0.1891477, 0.7079134],
[0.6346791, -0.2512092, 0.1913773, 0.7053027],
[0.6382542, -0.2504392, 0.1939134, 0.7016482],
[0.6421402, -0.2486396, 0.1979061, 0.6976163],
[0.6465912, -0.2450967, 0.2055614, 0.6925266],
[0.6499802, -0.2414217, 0.2123421, 0.688588],
[0.6550783, -0.2359805, 0.222261, 0.6824859],
[0.6584591, -0.233443, 0.2286426, 0.6779824],
[0.6629257, -0.2299991, 0.2384764, 0.671387],
[0.6659179, -0.2274206, 0.2458468, 0.6666288],
[0.6694705, -0.2242803, 0.2562658, 0.6601793],
[0.6722785, -0.2234074, 0.2664782, 0.6535452],
[0.6748305, -0.2227896, 0.2738837, 0.6480414],
[0.6816705, -0.2189832, 0.2829486, 0.638211],
[0.6908479, -0.2117589, 0.2894718, 0.6277699],
[0.7005658, -0.2010274, 0.2959344, 0.6174303],
[0.709353, -0.1881775, 0.3027278, 0.6080834],
[0.7176198, -0.1731782, 0.3102604, 0.5989757],
[0.7275901, -0.1537595, 0.3194358, 0.5873106],
[0.7364845, -0.1370744, 0.3288462, 0.5750338],
[0.7466617, -0.1192887, 0.3424163, 0.5576915],
[0.754434, -0.1078482, 0.3521214, 0.5433331],
[0.7663988, -0.0926975, 0.3629613, 0.5218251],
[0.7764621, -0.08112009, 0.3698685, 0.5037121],
[0.7859491, -0.07000248, 0.3747462, 0.4867768],
[0.796208, -0.05633906, 0.3787884, 0.4684024],
[0.8024514, -0.04540217, 0.3818861, 0.4562632],
[0.8106581, -0.02857927, 0.3860874, 0.4392674],
[0.817646, -0.01511704, 0.3897779, 0.423441],
[0.825356, -0.003776314, 0.3931201, 0.4052562],
[0.8361863, 0.006879332, 0.3951027, 0.3803183],
[0.8463783, 0.01487728, 0.3955642, 0.3563067],
[0.8556873, 0.02291882, 0.3967369, 0.331477],
[0.8652082, 0.0341625, 0.3970597, 0.3042932],
[0.8711935, 0.04480856, 0.3966036, 0.2858724],
[0.8787764, 0.06269402, 0.3955833, 0.2594974],
[0.884828, 0.07928419, 0.3943074, 0.2351989],
[0.8904272, 0.0948966, 0.3926672, 0.2096433],
[0.8956578, 0.108041, 0.3908611, 0.1826363],
[0.9013615, 0.1209637, 0.3878557, 0.1499577],
[0.9055435, 0.1320957, 0.3843445, 0.1217581],
[0.9095277, 0.1467415, 0.3785151, 0.08920016],
[0.9126568, 0.1597883, 0.3711409, 0.06151212],
[0.915319, 0.1712571, 0.3628456, 0.03477234],
[0.91781, 0.181395, 0.3531117, 0.00607161],
[0.9192696, 0.1882712, 0.3453511, -0.0152907],
[0.9202018, 0.1949337, 0.3378292, -0.03323983],
[0.9207498, 0.2014161, 0.3306879, -0.04796692],
[0.9210808, 0.2065599, 0.3244746, -0.06052513],
[0.9207444, 0.2111326, 0.3196048, -0.07422625],
[0.920416, 0.2129158, 0.3169443, -0.0839725],
[0.9203724, 0.212249, 0.3152047, -0.09227563],
[0.9208403, 0.2093063, 0.3138894, -0.09859425],
[0.9216852, 0.205283, 0.3129494, -0.1020845],
[0.9226816, 0.2017667, 0.3120895, -0.1027253],
[0.9237261, 0.1993438, 0.3112836, -0.1004879],
[0.9248617, 0.1971548, 0.3106166, -0.09633837],
[0.9259513, 0.1948489, 0.3107347, -0.08997535],
[0.926447, 0.1926425, 0.3119882, -0.0851576],
[0.9262999, 0.1895049, 0.3159405, -0.07900467],
[0.9253222, 0.1860272, 0.3221544, -0.07343832],
[0.9236129, 0.1817428, 0.3308499, -0.0667172],
[0.9213305, 0.1770991, 0.3411206, -0.05854105],
[0.918835, 0.1725413, 0.351611, -0.04843421],
[0.9159625, 0.1644999, 0.3642946, -0.03530715],
[0.913622, 0.1548671, 0.3752823, -0.0218826],
[0.9115435, 0.1416124, 0.3860154, -0.005563516],
[0.9093999, 0.1246011, 0.3965676, 0.01432137],
[0.9063191, 0.1020151, 0.4077272, 0.04406472],
[0.9035797, 0.08481656, 0.4138986, 0.07101078],
[0.8984175, 0.05894366, 0.4194586, 0.1158918],
[0.8917639, 0.0350965, 0.4217732, 0.1601173],
[0.8822384, 0.01115819, 0.4223648, 0.2077096],
[0.867295, -0.01592655, 0.4208535, 0.2653913],
[0.8507614, -0.0407969, 0.4185402, 0.3152291],
[0.8303204, -0.06822769, 0.4158427, 0.364675],
[0.8025976, -0.1006412, 0.4096109, 0.4218146],
[0.7797197, -0.1242195, 0.4034409, 0.462431],
[0.743759, -0.1553493, 0.3937778, 0.5173281],
[0.7093194, -0.1782001, 0.3843161, 0.5633938],
[0.6712515, -0.1971478, 0.3738074, 0.6089521],
[0.6234932, -0.2150149, 0.3598447, 0.6599525],
[0.5804691, -0.2290609, 0.345061, 0.7010849],
[0.5354696, -0.242798, 0.3272726, 0.7397395],
[0.4815227, -0.2589924, 0.3046306, 0.7799101],
[0.4427046, -0.2710079, 0.287983, 0.8047572],
[0.3875754, -0.2889804, 0.2650585, 0.8342785],
[0.3397629, -0.3029236, 0.2453238, 0.8559297],
[0.2924455, -0.3145408, 0.2254871, 0.8744689],
[0.2405785, -0.3236257, 0.2028732, 0.8923181],
[0.2017499, -0.3282014, 0.1850915, 0.9040591],
[0.1697293, -0.330268, 0.1685591, 0.9130738],
[0.1419657, -0.3305551, 0.1556259, 0.9199787],
[0.1255057, -0.3302169, 0.1480624, 0.9237337],
[0.1146405, -0.3316345, 0.1399818, 0.9258957],
[0.1020984, -0.3328722, 0.1338053, 0.9278306],
[0.08972573, -0.333162, 0.1318027, 0.9292911],
[0.06982366, -0.3326253, 0.1298343, 0.9314665],
[0.04855076, -0.3324758, 0.1270174, 0.9332581],
[0.03271631, -0.3323173, 0.124585, 0.9343312],
[0.01223762, -0.331733, 0.1210642, 0.9354938],
[-0.001296842, -0.3302855, 0.1221435, 0.9359448],
[-0.01173218, -0.3287683, 0.1235179, 0.9362261],
[-0.0215796, -0.3273272, 0.1264192, 0.9361688],
[-0.0293686, -0.3254157, 0.13246, 0.9357879],
[-0.03178336, -0.3234959, 0.140453, 0.9352089],
[-0.03104715, -0.3212514, 0.152096, 0.9341857],
[-0.02657295, -0.3175252, 0.1689874, 0.9326935],
[-0.02115158, -0.3129116, 0.1853801, 0.9312762],
[-0.01558153, -0.3064173, 0.2029825, 0.9298742],
[-0.01084849, -0.2991104, 0.2215174, 0.9280881],
[-0.005421336, -0.2925841, 0.2416138, 0.9251973],
[0.002138584, -0.2867033, 0.267713, 0.9198523],
[0.01018411, -0.2831774, 0.292686, 0.9132599],
[0.02072933, -0.2803648, 0.3206609, 0.9045133],
[0.0357857, -0.2766916, 0.3577149, 0.8911807],
[0.04700466, -0.2722692, 0.3880863, 0.8792329],
[0.06340598, -0.2627835, 0.4357984, 0.8584906],
[0.07996091, -0.2533487, 0.4778974, 0.8372793],
[0.09888311, -0.242899, 0.5184796, 0.8138815],
[0.1224763, -0.2306029, 0.564003, 0.7834055],
[0.1416343, -0.2215123, 0.6013566, 0.7544826],
[0.1588027, -0.2147717, 0.6366658, 0.7234038],
[0.1742438, -0.2108475, 0.6696568, 0.6904663],
[0.1901161, -0.2067758, 0.7059314, 0.6502016],
[0.2023682, -0.2027765, 0.7363876, 0.612914],
[0.2175784, -0.1986075, 0.7753487, 0.5586147],
[0.2279874, -0.1951726, 0.8028479, 0.5151365],
[0.2388688, -0.1892631, 0.8324476, 0.4627672],
[0.2477368, -0.1808973, 0.8588056, 0.4103133],
[0.2547425, -0.1702671, 0.8792376, 0.3647712],
[0.2636654, -0.1543106, 0.9002858, 0.3100896],
[0.2731385, -0.1355106, 0.9167129, 0.258208],
[0.2800292, -0.1139036, 0.9299055, 0.2094927],
[0.281584, -0.0929635, 0.9392434, 0.1728923],
[0.2777143, -0.06598353, 0.9484728, 0.137557],
[0.2685984, -0.03809468, 0.9561263, 0.1105804],
[0.2583002, -0.01651917, 0.9613391, 0.09400679],
[0.2443862, 0.005042297, 0.9663583, 0.08002123],
[0.2303291, 0.02343186, 0.9704023, 0.06870778],
[0.219769, 0.03792635, 0.9730411, 0.05879037],
[0.2113245, 0.05212439, 0.9748958, 0.04696078],
[0.2056598, 0.06332837, 0.9759517, 0.03484076],
[0.199014, 0.0773756, 0.9768393, 0.01391732],
[0.1956401, 0.08867642, 0.9766201, -0.008790608],
[0.1946928, 0.09651548, 0.9757063, -0.02791603],
[0.194301, 0.1020199, 0.9746349, -0.04391317],
[0.1937169, 0.1058475, 0.9736795, -0.05675212],
[0.1916288, 0.1092688, 0.9730968, -0.06651476],
[0.1879457, 0.1136776, 0.9727992, -0.07361029],
[0.1825249, 0.119874, 0.9724619, -0.08145821],
[0.1736567, 0.1267137, 0.9719272, -0.09564206],
[0.1552697, 0.1340009, 0.972092, -0.1139083],
[0.1389338, 0.1412075, 0.9718623, -0.1274543],
[0.1134769, 0.1537382, 0.9708763, -0.1445226],
[0.08231793, 0.168298, 0.9690942, -0.160487],
[0.05861261, 0.1799404, 0.9674425, -0.1680511],
[0.02769248, 0.1983657, 0.9643896, -0.1727337],
[0.00662356, 0.2155486, 0.9607494, -0.1745156],
[-0.011271, 0.2344345, 0.9558569, -0.1767802],
[-0.02115542, 0.2502716, 0.9505424, -0.182718],
[-0.02622791, 0.2661154, 0.9440956, -0.1928176],
[-0.0281366, 0.2790188, 0.937857, -0.2044055],
[-0.03346648, 0.2889466, 0.9320227, -0.216156],
[-0.04057269, 0.2948486, 0.927167, -0.2275509],
[-0.04917663, 0.2995968, 0.921041, -0.2439397],
[-0.05564688, 0.3030894, 0.9150051, -0.2603948],
[-0.06114172, 0.3095991, 0.9062185, -0.2813851],
[-0.05961048, 0.3184325, 0.8961847, -0.3031492],
[-0.04941577, 0.328573, 0.8826023, -0.3325808],
[-0.0307561, 0.3333871, 0.8711369, -0.3592028],
[0.0001497413, 0.3319947, 0.8572552, -0.3935636],
[0.032709, 0.3264606, 0.8437913, -0.4246989],
[0.06166545, 0.3206054, 0.8319877, -0.4485592],
[0.1021898, 0.3137732, 0.8148926, -0.4765007],
[0.1360031, 0.3091656, 0.7990627, -0.4974114],
[0.1682002, 0.3049283, 0.7829074, -0.5155413],
[0.2026436, 0.3023053, 0.7633076, -0.5337678],
[0.225306, 0.2975724, 0.7483482, -0.5483264],
[0.2396848, 0.2932288, 0.7376393, -0.5589771],
[0.2492709, 0.2889828, 0.7290628, -0.5681719],
[0.2557604, 0.2873206, 0.7236305, -0.5730543],
[0.2646212, 0.2858968, 0.7168522, -0.5782392],
[0.2753558, 0.282677, 0.7092069, -0.5842071],
[0.2841723, 0.2792034, 0.703743, -0.588249],
[0.3016696, 0.2735346, 0.6945347, -0.5931233],
[0.3184732, 0.2690372, 0.6876835, -0.5943775],
[0.3368148, 0.2662805, 0.6806141, -0.593645],
[0.3507388, 0.2640062, 0.6750637, -0.5929344],
[0.3582364, 0.2611051, 0.6734995, -0.5915138],
[0.3600352, 0.2592239, 0.6739269, -0.5907616],
[0.3578841, 0.2581888, 0.6747259, -0.5916092],
[0.3560519, 0.2577234, 0.6759261, -0.5915473],
[0.3541982, 0.2569073, 0.6778392, -0.5908256],
[0.3536958, 0.2553698, 0.6805503, -0.5886726],
[0.3529337, 0.2538466, 0.6843813, -0.5853382],
[0.3512836, 0.2527924, 0.6891768, -0.5811453],
[0.3479038, 0.2521715, 0.6952353, -0.5762109],
[0.3425948, 0.2520345, 0.7032338, -0.5697089],
[0.3362897, 0.2522607, 0.7130238, -0.5611321],
[0.3247805, 0.2526841, 0.7301003, -0.5455462],
[0.3146825, 0.2537032, 0.7460389, -0.5291827],
[0.3025295, 0.255796, 0.7678196, -0.5034842],
[0.2906139, 0.2587208, 0.7879221, -0.477268],
[0.2774442, 0.2626517, 0.8093457, -0.4460911],
[0.2640271, 0.2668127, 0.8300467, -0.4124589],
[0.250013, 0.2689111, 0.8521196, -0.3729236],
[0.2438529, 0.2673893, 0.8676875, -0.3408177],
[0.2457993, 0.2642933, 0.8790888, -0.3113423],
[0.2625529, 0.2580009, 0.8877997, -0.2762474],
[0.2808695, 0.2480266, 0.8953193, -0.2408278],
[0.2985225, 0.2341199, 0.9039761, -0.1972284],
[0.3153534, 0.2174017, 0.9121868, -0.1456142],
[0.3346378, 0.1961651, 0.9183235, -0.07885736],
[0.3505439, 0.1759206, 0.9196656, -0.01964238],
[0.363052, 0.1562911, 0.9181108, 0.02895596],
[0.3782639, 0.1266991, 0.9117789, 0.09758351],
[0.387495, 0.1014697, 0.9028109, 0.1564728],
[0.3943693, 0.07368501, 0.8876426, 0.226127],
[0.3983607, 0.05220667, 0.8701403, 0.2853746],
[0.4008709, 0.03095193, 0.8489688, 0.3429226],
[0.4029647, 0.00361151, 0.8198314, 0.4067955],
[0.4040239, -0.01908791, 0.7963181, 0.4497527],
[0.4018549, -0.05080661, 0.7663783, 0.4985932],
[0.3908256, -0.09716391, 0.7237746, 0.5603253],
[0.3707556, -0.1381917, 0.6848592, 0.6118911],
[0.3474656, -0.1709287, 0.6503804, 0.6534953],
[0.3152602, -0.2013901, 0.6070638, 0.7010894],
[0.2789134, -0.2223307, 0.5600529, 0.7477411],
[0.2457114, -0.234808, 0.5067955, 0.7922431],
[0.2222275, -0.2388012, 0.4554527, 0.8283426],
[0.1980797, -0.2380707, 0.3917982, 0.8663605],
[0.1776337, -0.2352278, 0.3260506, 0.8982235],
[0.1615765, -0.2342387, 0.2714625, 0.9194202],
[0.144244, -0.2344719, 0.2131765, 0.9374287],
[0.1324176, -0.2341794, 0.1684733, 0.948284],
[0.132492, -0.2299699, 0.1338722, 0.9547974],
[0.1386746, -0.2172393, 0.1041479, 0.9605883],
[0.1488311, -0.1981986, 0.07451828, 0.9659265],
[0.1611776, -0.1814854, 0.05510682, 0.968529],
[0.1717833, -0.1669462, 0.03596276, 0.9702199],
[0.1795936, -0.1550488, 0.01289842, 0.9713601],
[0.1843205, -0.1471395, -0.01069119, 0.9717318],
[0.187511, -0.1406116, -0.03800659, 0.9714034],
[0.1916131, -0.1351424, -0.06741998, 0.9697815],
[0.1968032, -0.1303866, -0.09810159, 0.9667701],
[0.2047324, -0.1280878, -0.1353796, 0.9609116],
[0.2107412, -0.1270687, -0.1621418, 0.9555899],
[0.2200275, -0.1225445, -0.2001808, 0.9468362],
[0.2275796, -0.1146205, -0.2373349, 0.9374124],
[0.2288021, -0.1047532, -0.2726517, 0.9286212],
[0.2256343, -0.08799561, -0.3175903, 0.9167782],
[0.2193027, -0.06819362, -0.3638254, 0.9027109],
[0.213738, -0.05493456, -0.3975189, 0.8906609],
[0.2045454, -0.04243778, -0.4418284, 0.8724378],
[0.1932365, -0.03891916, -0.4778145, 0.8560594],
[0.1795132, -0.04103631, -0.5122091, 0.8388877],
[0.1604548, -0.04871625, -0.5499136, 0.818215],
[0.1429054, -0.05675196, -0.5792452, 0.8005197],
[0.1249777, -0.06479706, -0.6050867, 0.7836144],
[0.1044307, -0.0736222, -0.6315795, 0.7647097],
[0.09096152, -0.08036552, -0.6497036, 0.7504345],
[0.07561959, -0.09217198, -0.6756843, 0.727486],
[0.067008, -0.1046976, -0.6988505, 0.704383],
[0.06093413, -0.1193619, -0.7212343, 0.6796027],
[0.05500149, -0.1348528, -0.7410157, 0.6555031],
[0.04648862, -0.1535611, -0.760806, 0.6288332],
[0.03798283, -0.1698465, -0.7759811, 0.6062689],
[0.0268621, -0.1886497, -0.792675, 0.5790986],
[0.01640578, -0.203475, -0.8067381, 0.5545283],
[0.003478762, -0.218088, -0.8231065, 0.5243285],
[-0.005772026, -0.2267631, -0.83467, 0.5018669],
[-0.01671384, -0.2357008, -0.8478681, 0.4746417],
[-0.02839377, -0.2437605, -0.8620558, 0.4434341],
[-0.03687165, -0.2481389, -0.873575, 0.4170537],
[-0.04549794, -0.2498955, -0.8861355, 0.3876149],
[-0.05192456, -0.2488927, -0.8960047, 0.3640483],
[-0.05600236, -0.2465979, -0.9035839, 0.345816],
[-0.05902683, -0.2416411, -0.9130467, 0.3232194],
[-0.05893096, -0.2367304, -0.9197518, 0.3074773],
[-0.05590979, -0.2318063, -0.925249, 0.2950494],
[-0.0478234, -0.2263931, -0.9299458, 0.2857624],
[-0.03790183, -0.2209593, -0.9328293, 0.2820816],
[-0.02622432, -0.2159256, -0.9340932, 0.2831228],
[-0.01298447, -0.210774, -0.9336588, 0.2892875],
[-0.002860504, -0.2077385, -0.9318205, 0.2975694],
[0.005663036, -0.2061428, -0.9293963, 0.3060977],
[0.01279712, -0.2053325, -0.9268116, 0.3141581],
[0.01884309, -0.2044683, -0.9241285, 0.322218],
[0.02431183, -0.2031047, -0.9203328, 0.3333846],
[0.02822888, -0.2011465, -0.9159001, 0.3462235],
[0.03245094, -0.1981051, -0.9097723, 0.36334],
[0.03794913, -0.1946341, -0.9009116, 0.3860517],
[0.04708961, -0.1899421, -0.8864745, 0.4193659],
[0.05905867, -0.1847275, -0.8669003, 0.4592083],
[0.06808927, -0.1815849, -0.8492814, 0.4910319],
[0.07920942, -0.1784338, -0.8246698, 0.5308555],
[0.09365951, -0.1760225, -0.786418, 0.5846293],
[0.1043197, -0.1750441, -0.7545511, 0.6238031]]

# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib.animation import FuncAnimation
#
# def slerp(q1, q2, t):
#     dot_product = np.dot(q1, q2)
#
#     if dot_product < 0.0:
#         q1 = -q1
#         dot_product = -dot_product
#
#     omega = np.arccos(dot_product)
#
#     if np.abs(omega) < 1e-5:
#         result = (1.0 - t) * q1 + t * q2
#     else:
#         sin_omega = np.sin(omega)
#         result = (np.sin((1.0 - t) * omega) / sin_omega) * q1 + (np.sin(t * omega) / sin_omega) * q2
#
#     return result
#
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
# from scipy.spatial.transform import Rotation
#
# def slerp(q1, q2, t):
#     q1 = Rotation.from_quat(q1)
#     q2 = Rotation.from_quat(q2)
#     intermediate = Rotation.slerp(q1, q2, t)
#     return intermediate.as_quat()
#
# def animate_slerp(quaternions, frames=100):
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')
#     ax.set_xlim([-1, 1])
#     ax.set_ylim([-1, 1])
#     ax.set_zlim([-1, 1])
#
#     def update(frame):
#         ax.cla()
#         ax.set_xlim([-1, 1])
#         ax.set_ylim([-1, 1])
#         ax.set_zlim([-1, 1])
#         ax.set_title(f'Frame {frame}/{frames}')
#
#         t = frame / frames
#         interpolated_quaternion = slerp(quaternions[0], quaternions[-1], t)
#
#         # Plot the interpolated quaternion
#         ax.quiver(0, 0, 0, *interpolated_quaternion, color='r', label='Interpolated')
#
#         # Plot the original quaternions
#         for q in quaternions:
#             ax.quiver(0, 0, 0, *q, color='b', alpha=0.2)
#
#     ani = FuncAnimation(fig, update, frames=frames, interval=50)
#     plt.show()
#
# animate_slerp(quaternions_list)
#
