from direct.directtools.DirectGeometry import LineNodePath

from panda3d.core import Material, NodePath, PandaNode


def make_empty(name='Empty', size=0.1, parent=None):
    empty = NodePath(PandaNode(name))

    red = Material()
    red.set_base_color((1, 0, 0, 1))
    green = Material()
    green.set_base_color((0, 1, 0, 1))
    blue = Material()
    blue.set_base_color((0, 0, 1, 1))

    line_x = LineNodePath(thickness=2.0, colorVec=(1, 0, 0, 1))
    line_x.drawLines((
        ((0, 0, 0), (size, 0, 0)),  # x
    ))
    line_x.create()
    line_x.set_material(red)
    line_x.reparent_to(empty)

    line_y = LineNodePath(thickness=2.0, colorVec=(0, 1, 0, 1))
    line_y.drawLines((
        ((0, 0, 0), (0, size, 0)),  # y
    ))
    line_y.create()
    line_y.set_material(green)
    line_y.reparent_to(empty)

    line_z = LineNodePath(thickness=2.0, colorVec=(0, 0, 1, 1))
    line_z.drawLines((
        ((0, 0, 0), (0, 0, size)),  # z
    ))
    line_z.create()
    line_z.set_material(blue)
    line_z.reparent_to(empty)

    if parent:
        empty.reparent_to(parent)

    return empty
