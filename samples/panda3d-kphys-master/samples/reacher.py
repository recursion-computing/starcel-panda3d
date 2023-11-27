"""
Based on sample from
https://github.com/Germanunkol/CCD-IK-Panda3D/blob/master/ReacherSample.py
"""

if __name__ == "__main__":
    import math
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import load_prc_file_data, NodePath, LVector3f, WindowProperties
    from kphys.core import ArmatureNode, BoneNode, EffectorNode, IK_ENGINE_CCDIK
    from common import make_empty

    class MyApp(ShowBase):

        def __init__(self):
            load_prc_file_data('', 'framebuffer-alpha f')

            ShowBase.__init__(self)
            # base.disableMouse()
            base.setFrameRateMeter(True)

            wp = WindowProperties()
            wp.setSize(1800, 960)
            self.win.requestProperties(wp)

            base.setBackgroundColor(0,0,0)

            # grid = createGrid( 20, 1 )
            # render.attachNewNode( grid )
            # axes = createAxes( 1000, bothways=True, thickness=3 )
            # render.attachNewNode( axes )

            root = render.attachNewNode("Root")
            root.setPos( 1, 1, 1 )

            #######################################
            ## Set up the joints:
            actor = NodePath(ArmatureNode('Armature'))

            joint = None
            for i in range( 6 ):
                offsetLength = 0.5
                if i == 0:
                    offsetLength = 0.1
                joint = (joint or actor).attachNewNode(BoneNode(f"joint{i}", bone_id=i))
                joint.set_x(offsetLength)

            ## IMPORTANT! Attach the created actor to the scene, otherwise you won't see anything!
            actor.reparentTo( render )
            self.actor = actor

            #######################################
            ## Create an IK chain from the armature:

            bone = None
            for i in range( 6 ):
                name = f"joint{i}"
                joint = actor.find(f'**/{name}')
                if i < 4:
                    joint.node().set_hinge_constraint(LVector3f.unitZ(),
                            min_ang=-math.pi*0.25, max_ang=math.pi*0.25 )
                else:
                    joint.node().set_hinge_constraint(LVector3f.unitY(),
                            min_ang=-math.pi*0.25, max_ang=math.pi*0.25 )


            ############################################
            ## Set up camera:
            # focusNode = render.attachNewNode( "CameraFocusNode" )
            # self.camControl = CameraControl( camera, self.mouseWatcherNode )

            # self.taskMgr.add( self.camControl.moveCamera, "MoveCameraTask")

            self.cam.set_pos(0, -7.07107, 7.57107)
            self.cam.set_p(-45)

            ##################################
            ## Target point:

            # point = createPoint( thickness=10 )

            self.ikTarget = joint.attachNewNode(EffectorNode('Target', chain_length=5))
            self.ikTarget.setPos(render, 2,0,2 )

            for bone in actor.find_all_matches('**/+BoneNode'):
                make_empty(parent=bone)
            for bone in actor.find_all_matches('**/+EffectorNode'):
                make_empty(parent=bone)

            actor.node().rebuild_bind_pose()
            actor.node().rebuild_ik(IK_ENGINE_CCDIK)

            self.taskMgr.add( self.moveTarget, "MoveTarget" )

            ############################################
            ## Set up controls:

            # self.accept( "wheel_down", self.camControl.wheelDown )
            # self.accept( "wheel_up", self.camControl.wheelUp )

            self.accept( "p", self.toggleAnimation )
            self.animateTarget = True

            # self.accept( "r", self.toggleRacket )
            # self.racket = None

            # label("[WASD]: Move Camera", 1)
            # label("[Mouse Wheel]: Zoom Camera", 2)
            # label("[Middle Mouse]: Rotate Camera", 3)
            # label("[P]: Pause Animation", 5)
            # label("[R]: Attach a racket to the end effector bone", 7)

        def moveTarget( self, task ):
            if self.animateTarget:
                speed = 1
                self.ikTarget.setPos(
                        render,
                        4*math.sin(speed*task.time*1.6+2),
                        2.5*math.sin(speed*task.time),
                        math.cos(speed*task.time*1.6+2) )

            # self.actor.node().reset()
            self.actor.node().update_ik()
            return task.cont

        # def toggleRacket( self ):
        #     if self.racket:
        #         self.racket.removeNode()
        #         self.racket = None
        #     else:
        #         self.racket = createRacket()
        #         endEffector = self.ikChain.getBone( "joint5" )
        #         self.racket.reparentTo( endEffector.controlNode )



        def toggleAnimation( self ):
            self.animateTarget = (self.animateTarget == False)


    app = MyApp()
    app.run()
