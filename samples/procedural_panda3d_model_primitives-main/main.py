# Author: Epihaius
# Date: 2021-06-18
#
# This sample generates one of each of the available 3D primitive types.

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from procedural3d import *


base = ShowBase()


# set up a light source
light_node = PointLight("point_light")
light_node.set_color((1., 1., 1., 1.))
light = base.camera.attach_new_node(light_node)
light.set_pos(5., -10., 7.)
base.render.set_light(light)


# Generate 3D primitives, one of each type.

box_maker = BoxMaker(
    center=(0., 0., 0.),
    width=2.,
    depth=2.,
    height=2.,
    segments={
        "width": 2,
        "depth": 4,
        "height": 3
    },
    open_sides=("left", "back", "top"),
    thickness=.45,
    inverted=False,
    vertex_color=None,
    has_uvs=True,
    tex_offset={
        "left": (.5, .5),
        "back": (.5, .5),
        "bottom": (.5, .5)
    },
    tex_scale={
        "left": (.5, .5),
        "right": (.5, .5),
        "back": (.5, .5),
        "front": (.5, .5),
        "bottom": (.5, .5),
        "top": (.5, .5)
    }
)
box = base.render.attach_new_node(box_maker.generate())
box.set_render_mode_filled_wireframe((1., 0., 0., 1.))

sphere_maker = SphereMaker(
    center=(0., 0., -.7),
    radius=2.,
    segments={
        "horizontal": 40,
        "vertical": 10,
        "bottom_cap": 3,
        "top_cap": 3,
        "slice_caps": 2
    },
    smooth=True,
    bottom_clip=.1,
    top_clip=.8,
    slice=125.,
    thickness=.2,
    inverted=False,
    vertex_color=None,
    has_uvs=True,
    tex_units={
        "main": (6., 6.),
        "inner_main": (6., 6.),
        "bottom_cap": (6., 6.),
        "top_cap": (6., 6.),
        "inner_bottom_cap": (6., 6.),
        "inner_top_cap": (6., 6.),
        "slice_start_cap": (6., 6.),
        "slice_end_cap": (6., 6.)
    },
    tex_offset={
        "slice_start_cap": (.2, 0.)
    },
    tex_rotation={
        "main": 20.,
        "inner_main": -40.,
        "bottom_cap": 160.,
        "inner_bottom_cap": 160.,
        "slice_start_cap": 90.,
        "slice_end_cap": 60.
    },
    tex_scale={
        "slice_end_cap": (1.5, 1.5)
    }
)
sphere = base.render.attach_new_node(sphere_maker.generate())
sphere.set_render_mode_filled_wireframe((1., 0., 0., 1.))
sphere.set_x(-5.)
sphere.set_h(-150.)

cylinder_maker = CylinderMaker(
    bottom_center=(-.5, .3, .2),
    top_center=(.5, -.4, -.3),
    radius=2.,
    segments={
        "circular": 40,
        "axial": 5,
        "bottom_cap": 3,
        "top_cap": 2,
        "slice_caps_radial": 3,
        "slice_caps_axial": 2
    },
    smooth=True,
    slice=125.,
    rotation=60.,
    thickness=.5,
    inverted=False,
    vertex_color=None,
    has_uvs=True,
    tex_units={
        "main": (6., 6.),
        "inner_main": (6., 6.),
        "bottom_cap": (6., 6.),
        "top_cap": (6., 6.),
        "slice_start_cap": (6., 6.),
        "slice_end_cap": (6., 6.)
    },
    tex_offset={
        "slice_start_cap": (.2, 0.)
    },
    tex_rotation={
        "inner_main": 10.,
        "bottom_cap": 160.,
        "slice_start_cap": 160.,
        "slice_end_cap": 60.
    },
    tex_scale={
        "slice_end_cap": (1.5, 1.5)
    }
)
cylinder = base.render.attach_new_node(cylinder_maker.generate())
cylinder.set_render_mode_filled_wireframe((1., 0., 0., 1.))
cylinder.set_x(5.)

cone_maker = ConeMaker(
    bottom_center=None,
    top_center=(0., 0., 1.),
    bottom_radius=2.,
    top_radius=2.2,
    segments={
        "circular": 10,
        "axial": 4,
        "bottom_cap": 3,
        "top_cap": 2,
        "slice_caps_radial": 5,
        "slice_caps_axial": 3
    },
    smooth=False,
    slice=105.,
    rotation=-70.,
    bottom_thickness=1.,
    top_thickness=1.4,
    inverted=False,
    vertex_color=None,
    has_uvs=True,
    tex_units={
        "main": (6., 6.),
        "inner_main": (6., 6.),
        "bottom_cap": (6., 6.),
        "top_cap": (6., 6.),
        "slice_start_cap": (6., 6.),
        "slice_end_cap": (6., 6.)
    },
    tex_offset={
        "slice_start_cap": (.2, 0.)
    },
    tex_rotation={
        "inner_main": 10.,
        "bottom_cap": 160.,
        "slice_start_cap": 160.,
        "slice_end_cap": 60.
    },
    tex_scale={
        "slice_end_cap": (1.5, 1.5)
    }
)
cone = base.render.attach_new_node(cone_maker.generate())
cone.set_render_mode_filled_wireframe((1., 0., 0., 1.))
cone.set_x(-10.)

torus_maker = TorusMaker(
    center=None,
    ring_radius=2.6,
    section_radius=1.,
    segments={
        "ring": 200,
        "section": 5,
        "ring_slice_start_cap": 2,
        "ring_slice_end_cap": 3,
        "section_slice_start_cap": 3,
        "section_slice_end_cap": 2
    },
    smooth_ring=True,
    smooth_section=False,
    ring_slice=125.,
    section_slice=125.,
    rotation=20.,
    twist=-550.,
    thickness=.5,
    inverted=False,
    vertex_color=None,
    has_uvs=True,
    tex_units={
        "main": (6., 6.),
        "inner_main": (6., 6.),
        "section_slice_start_cap": (6., 6.),
        "section_slice_end_cap": (6., 6.),
        "ring_slice_start_cap": (6., 6.),
        "ring_slice_end_cap": (6., 6.)
    }
)
torus = base.render.attach_new_node(torus_maker.generate())
torus.set_render_mode_filled_wireframe((1., 0., 0., 1.))
torus.set_x(12.)


base.run()
