from direct.showbase.ShowBase import ShowBase
from panda3d.core import PointLight, AmbientLight
from panda3d.core import Vec4
from panda3d.core import Shader
from panda3d.core import GraphicsStateGuardianBase, SamplerState
from direct.showbase.BufferViewer import BufferViewer

SHADOW_NEAR = 5
SHADOW_FAR = 100

class MyApp(ShowBase):

    def __init__(self):

        ShowBase.__init__(self)

        # Load the environment model.
        self.scene = self.loader.loadModel("environment.egg")

        # Reparent the model to render.
        self.scene.reparentTo(self.render)

        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        # Set up point light that will cast shadows:
        plight = PointLight('plight')
        plight.setColorTemperature( 3600 )
        plight.setShadowCaster(True, 256, 256)
        plnp = render.attachNewNode(plight)
        plnp.setPos(0, 0, 20)
        render.setLight(plnp)
        self.plight = plight

        for i in range(6):
            plight.getLens(i).setNear(SHADOW_NEAR)
            plight.getLens(i).setFar(SHADOW_FAR)

        # Let environment receive shadows:
        self.init_shaders()
        self.accept("v", base.bufferViewer.toggleEnable)

        self.filter_mode = "LINEAR"
        
        taskMgr.doMethodLater(1, self.toggle_texture_filter_mode, 'toggle filter mode')

    def init_shaders(self):

        shader = Shader.load(Shader.SL_GLSL, "shadow_receiver.vert", "shadow_receiver.frag")
        self.scene.setShader(shader)
        self.scene.set_two_sided(True)
        self.scene.set_shader_input("NEAR", SHADOW_NEAR)
        self.scene.set_shader_input("FAR", SHADOW_FAR)
        #self.scene.ls()


    def toggle_texture_filter_mode(self, task):
        # Try to fix Filter mode for texture:
        sBuffer = self.plight.getShadowBuffer( GraphicsStateGuardianBase.getGsg(0) )
        if sBuffer is not None:
            tex = sBuffer.getTexture()
            print("Texture settings (before):", tex)

            state = tex.default_sampler
            # Create mutable copy:
            state = SamplerState( state )
            print(self.filter_mode)
            if self.filter_mode == "SHADOW":
                pass
                #state.setMinfilter( SamplerState.FT_linear )
                #state.setMagfilter( SamplerState.FT_linear )
                #self.filter_mode = "LINEAR"
            else:
                state.setMinfilter( SamplerState.FT_shadow )
                state.setMagfilter( SamplerState.FT_shadow )
                self.filter_mode = "SHADOW"
            tex.setDefaultSampler( state )
            print("Texture settings (after):", tex)
            print("EffectiveMinFilter:", tex.getEffectiveMinfilter())
            print("EffectiveMagFilter:", tex.getEffectiveMagfilter())
        return task.again



app = MyApp()
app.run()
