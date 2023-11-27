from ursina import *

app = Ursina()

# # Render Pipeline setup
# sys.path.insert(0, "../../")
# sys.path.insert(0, "../../RenderPipeline")
#
#
# from rpcore import RenderPipeline, SpotLight
#
# render_pipeline = RenderPipeline()
# render_pipeline.pre_showbase_init()
# render_pipeline.create(app)
# from rpcore.util.movement_controller import MovementController
#
#
# # Init movement controller
# controller = MovementController(app)
# controller.setup()
# # Set time of day
# render_pipeline.daytime_mgr.time = 1

model = loader.load_model("DroneSphere.blend")#scene/Scene.bam")
model.reparent_to(render)

app.run()
