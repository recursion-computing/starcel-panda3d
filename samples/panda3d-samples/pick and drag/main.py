'''
Picker class for Panda3d.

Created on Oct 31, 2017

@author: consultit
'''

from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionNode, CollisionRay, \
    BitMask32, LPoint3f, NodePath, CardMaker
from direct.showbase.ShowBase import ShowBase

class Picker(object):
    '''
    A class for picking (Panda3d) objects.
    '''

    def __init__(self, app, render, camera, mouseWatcher, pickKeyOn, pickKeyOff, collideMask,
                 pickableTag="pickable"):
        self.render = render
        self.mouseWatcher = mouseWatcher.node()
        self.camera = camera
        self.camLens = camera.node().get_lens()
        self.collideMask = collideMask
        self.pickableTag = pickableTag
        self.taskMgr = app.task_mgr
        # setup event callback for picking body
        self.pickKeyOn = pickKeyOn
        self.pickKeyOff = pickKeyOff
        app.accept(self.pickKeyOn, self._pickBody, [self.pickKeyOn])
        app.accept(self.pickKeyOff, self._pickBody, [self.pickKeyOff])
        # collision data
        self.collideMask = collideMask
        self.cTrav = CollisionTraverser()
        self.collisionHandler = CollisionHandlerQueue()
        self.pickerRay = CollisionRay()
        pickerNode = CollisionNode("Utilities.pickerNode")
        pickerNode.add_solid(self.pickerRay)
        pickerNode.set_from_collide_mask(self.collideMask)
        pickerNode.set_into_collide_mask(BitMask32.all_off())
        self.cTrav.add_collider(self.render.attach_new_node(pickerNode), self.collisionHandler)
        # service data
        self.pickedBody = None
        self.oldPickingDist = 0.0
        self.deltaDist = 0.0
        self.dragging = False
        self.updateTask = None

    def _pickBody(self, event):
        # handle body picking
        if event == self.pickKeyOn:
            # check mouse position
            if self.mouseWatcher.has_mouse():
                # Get to and from pos in camera coordinates
                pMouse = self.mouseWatcher.get_mouse()
                #
                pFrom = LPoint3f()
                pTo = LPoint3f()
                if self.camLens.extrude(pMouse, pFrom, pTo):
                    # Transform to global coordinates
                    rayFromWorld = self.render.get_relative_point(self.camera, pFrom)
                    rayToWorld = self.render.get_relative_point(self.camera, pTo)
                    # cast a ray to detect a body
                    # traverse downward starting at rayOrigin
                    self.pickerRay.set_direction(rayToWorld - rayFromWorld)
                    self.pickerRay.set_origin(rayFromWorld)
                    self.cTrav.traverse(self.render)
                    if self.collisionHandler.get_num_entries() > 0:
                        self.collisionHandler.sort_entries()
                        entry0 = self.collisionHandler.get_entry(0)
                        hitPos = entry0.get_surface_point(self.render)
                        # get the first parent with name
                        pickedObject = entry0.get_into_node_path()
                        while not pickedObject.has_tag(self.pickableTag):
                            pickedObject = pickedObject.getParent()
                            if not pickedObject:
                                return
                            if pickedObject == self.render:
                                return
                        #
                        self.pickedBody = pickedObject
                        self.oldPickingDist = (hitPos - rayFromWorld).length()
                        self.deltaDist = (self.pickedBody.get_pos(self.render) - hitPos)
                        print(self.pickedBody.get_name(), hitPos)
                        if not self.dragging:
                            self.dragging = True
                            # create the task for updating picked body motion
                            self.updateTask = self.taskMgr.add(self._movePickedBody,
                                                                    "_movePickedBody")
                            # set sort/priority
                            self.updateTask.set_sort(0)
                            self.updateTask.set_priority(0)
        else:
            if self.dragging:
                # remove pick body motion update task
                self.taskMgr.remove("_movePickedBody")
                self.updateTask = None
                self.dragging = False
                self.pickedBody = None

    def _movePickedBody(self, task):
        # handle picked body if any
        if self.pickedBody and self.dragging:
            # check mouse position
            if self.mouseWatcher.has_mouse():
                # Get to and from pos in camera coordinates
                pMouse = self.mouseWatcher.get_mouse()
                #
                pFrom = LPoint3f()
                pTo = LPoint3f()
                if self.camLens.extrude(pMouse, pFrom, pTo):
                    # Transform to global coordinates
                    rayFromWorld = self.render.get_relative_point(self.camera, pFrom)
                    rayToWorld = self.render.get_relative_point(self.camera, pTo)
                    # keep it at the same picking distance
                    direction = (rayToWorld - rayFromWorld).normalized()
                    direction *= self.oldPickingDist
                    self.pickedBody.set_pos(self.render, rayFromWorld + direction + self.deltaDist)
        #
        return task.cont

if __name__ == "__main__":
    app = ShowBase()

    # create the picker
    PICKABLETAG = "pickable"
    PICKKEYON = "mouse3"
    PICKKEYOFF = "mouse3-up"
    picker = Picker(app, app.render, app.cam, app.mouseWatcher, PICKKEYON, PICKKEYOFF,
                    BitMask32.all_on(), PICKABLETAG)

    # some scene data
    numR = 3
    numC = 3
    dist = 5
    dimRMin = -((numR - 1) * dist) / 2.0
    dimCMin = -((numC - 1) * dist) / 2.0
    # ground
    cm = CardMaker("ground")
    left, right, bottom, top = dimCMin * 1.1, -dimCMin * 1.1, dimRMin * 1.1, -dimRMin * 1.1
    cm.setFrame(left, right, bottom, top)
    ground = app.render.attach_new_node(cm.generate())
    ground.set_pos(0, 0, 0)
    ground.set_p(-90)
    ground.set_color(0.2, 0.6, 0.4, 1)
    ground.set_tag(PICKABLETAG, "")


    panda = app.loader.load_model("Cylinder.bam")
    panda.reparent_to(app.render)
    panda.set_pos(0, 0, 6)
    panda.set_scale(0.5)
    panda.set_tag(PICKABLETAG, "")


    model = app.loader.load_model("coordinate2.bam")
    for r in range(numR):
        for c in range(numC):
            modelInst = NodePath("model_" + str(r) + "_" + str(c))
            model.instance_to(modelInst)
            modelInst.reparent_to(app.render)
            modelInst.set_pos(dimCMin + dist * c, dimRMin + dist * r, 3)
            modelInst.set_tag(PICKABLETAG, "")
    # setup camera
#     trackball = app.trackball.node()
#     trackball.set_pos(0.0, max(-dimRMin * 2, -dimCMin * 2) * 2, -2.0)
#     trackball.set_hpr(0.0, 25.0, 0.0)
    app.disable_mouse()
    app.camera.set_pos(0.0, max(dimRMin * 2, dimCMin * 2) * 3, 8.0)
    app.camera.set_hpr(0.0, -5.0, 0.0)
    # run
    app.run()