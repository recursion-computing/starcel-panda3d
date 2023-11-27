from ursinanetworking import *
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import threading
import time
from random import randint
from panda3d.core import Vec3, load_prc_file_data, Material
from shared import *
# Render Pipeline setup
sys.path.insert(0, "../../../")
sys.path.insert(0, "../../../RenderPipeline")
# from panda3d.core import loadPrcFile
# loadPrcFile("config.prc")

from rpcore import RenderPipeline, SpotLight

render_pipeline = RenderPipeline()
# render_pipeline.pre_showbase_init()

app = Ursina(render_pipeline=render_pipeline)


window.borderless = False

Client = UrsinaNetworkingClient("localhost", 25565)
Blabla = ReplicatedClEventsHandler(Client)

# PointLight(position = (4, 1, 4))

#
# render_pipeline.create(app)

# Set time of day
#render_pipeline.daytime_mgr.time = 1
#
# from ursina.shaders import lit_with_shadows_shader
# Entity.default_shader = lit_with_shadows_shader

# Generate temperature lamps
# This shows how to procedurally create lamps. In this case, we
# base the lights positions on empties created in blender.
# Load the scene
#from ursina.shaders import lit_with_shadows_shader
# Entity.default_shader = lit_with_shadows_shader
model = loader.loadModel("scene/TestScene.bam")
model.reparent_to(render)
# model = Entity(model="scene/TestScene.bam")#"DroneSphere.blend")
#model = loader.load_model("scene/Scene.bam")
#model.reparent_to(render)

# half_energy = 5000
# lamp_fov = 70
# lamp_radius = 10
# _lights = []
# light_key = lambda light: int(light.get_name().split("LampLum")[-1])
# lumlamps = sorted(model.find_all_matches("**/LampLum*"), key=light_key)
# for lumlamp in lumlamps:
#     lum = float(lumlamp.get_name()[len("LampLum"):])
#     light = SpotLight()
#     light.direction = (0, -1.5, -1)
#     light.fov = lamp_fov
#     light.set_color_from_temperature(lum * 1000.0)
#     light.energy = half_energy
#     light.pos = lumlamp.get_pos(render)
#     light.radius = lamp_radius
#     light.casts_shadows = False
#     light.shadow_map_resolution = 256
#     render_pipeline.add_light(light)
#
#     # Put Pandas on the edges
#     if lumlamp in lumlamps[0:2] + lumlamps[-2:]:
#         panda = loader.load_model("panda")
#         panda.reparent_to(render)
#         panda_mat = Material("default")
#         panda_mat.emission = 0
#         panda.set_material(panda_mat)
#         panda.set_pos(light.pos)
#         panda.set_z(0.65)
#         panda.set_h(180 + randint(-60, 60))
#         panda.set_scale(0.2)
#         panda.set_y(panda.get_y() - 3.0)
#
#     _lights.append(light)

def update():
    Client.process_net_events()
    Blabla.replicated_update()

player = FirstPersonController()
app.run()