import struct

from direct.stdpy.file import open as dopen

from panda3d.core import (
    CS_zup_right, CullFaceAttrib, Light, LMatrix4, LQuaternion,
    NodePath, ModelRoot, PandaNode, TransformState)

from gltf.converter import Converter, HAVE_BULLET, get_extras
from gltf.parseutils import parse_glb_data, parse_gltf_data

from .core import ArmatureNode, BoneNode


class DummyCharacter(object):
    bundles = []


class KPhysConverter(Converter):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._joint_ids = {}  # node id to joint index mapping
        self._mesh2joint = {}  # mesh node id to joint node id mapping

    def load_skin(self, skinid, gltf_skin, gltf_data):
        # child to parent mapping
        parents = {}
        for i, node in enumerate(gltf_data['nodes']):
            for child in node.get('children', ()):
                parents[child] = i

        # search for the root bone
        for i in gltf_skin['joints']:
            if parents.get(i) not in gltf_skin['joints']:  # no parent bone
                self.skeletons[i] = skinid
                break

    def build_character(self, char, nodeid, jvtmap, cvsmap, gltf_data, recurse=True):
        super().build_character(
            DummyCharacter(), nodeid,
            jvtmap, cvsmap, gltf_data, recurse=recurse)

    def build_character_sliders(self, *args, **kw):
        return {}

    def build_character_joints(self, char, root_nodeids, affected_nodeids, skinid, gltf_data):
        gltf_skin = gltf_data['skins'][skinid]

        def create_joint(nodeid):
            node = gltf_data['nodes'][nodeid]

            if nodeid in gltf_skin['joints']:
                joint_index = gltf_skin['joints'].index(nodeid)
                self._joint_ids[nodeid] = joint_index

            for child in node.get('children', []):
                create_joint(child)

        for root_nodeid in root_nodeids:
            create_joint(root_nodeid)

        return {}

    def update(self, gltf_data):
        #pprint.pprint(gltf_data)

        skip_axis_conversion = (
            'extensionsUsed' in gltf_data and 'BP_zup' in gltf_data['extensionsUsed'] or
            self.settings.skip_axis_conversion
        )

        if skip_axis_conversion:
            self.csxform = LMatrix4.ident_mat()
            self.csxform_inv = LMatrix4.ident_mat()
            self.compose_cs = CS_zup_right

        # Convert data
        for buffid, gltf_buffer in enumerate(gltf_data.get('buffers', [])):
            self.load_buffer(buffid, gltf_buffer)

        for camid, gltf_cam in enumerate(gltf_data.get('cameras', [])):
            self.load_camera(camid, gltf_cam)

        if 'extensions' in gltf_data and 'KHR_lights' in gltf_data['extensions']:
            lights = gltf_data['extensions']['KHR_lights'].get('lights', [])
            for lightid, gltf_light in enumerate(lights):
                self.load_light(lightid, gltf_light)

        if 'extensions' in gltf_data and 'KHR_lights_punctual' in gltf_data['extensions']:
            lights = gltf_data['extensions']['KHR_lights_punctual'].get('lights', [])
            for lightid, gltf_light in enumerate(lights):
                self.load_light(lightid, gltf_light, punctual=True)

        for texid, gltf_tex in enumerate(gltf_data.get('textures', [])):
            self.load_texture(texid, gltf_tex, gltf_data)
        self.load_fallback_texture()

        for matid, gltf_mat in enumerate(gltf_data.get('materials', [])):
            self.load_material(matid, gltf_mat)

        for skinid, gltf_skin in enumerate(gltf_data.get('skins', [])):
            self.load_skin(skinid, gltf_skin, gltf_data)

        for meshid, gltf_mesh in enumerate(gltf_data.get('meshes', [])):
            self.load_mesh(meshid, gltf_mesh, gltf_data)

        # Build scenegraphs
        def add_node(root, gltf_scene, nodeid, jvtmap, cvsmap):
            try:
                gltf_node = gltf_data['nodes'][nodeid]
            except IndexError:
                print("Could not find node with index: {}".format(nodeid))
                return

            scene_extras = get_extras(gltf_scene)
            node_name = gltf_node.get('name', 'node'+str(nodeid))
            if nodeid in self._joint_nodes:
                # Handle non-joint children of joints, but don't add joints themselves
                for child_nodeid in gltf_node.get('children', []):
                    add_node(root, gltf_scene, child_nodeid, jvtmap, cvsmap)
                return

            jvtmap = dict(jvtmap)
            cvsmap = dict(cvsmap)

            if nodeid in self.skeletons:
                # This node is the root of an animated character.
                # panda_node = Character(node_name)
                # prebuild character data
                self.build_character(None, nodeid, {}, {}, gltf_data, recurse=False)
            if nodeid in self._joint_ids:
                panda_node = BoneNode(node_name, self._joint_ids[nodeid])
            else:
                panda_node = PandaNode(node_name)

            # Determine the transformation.
            if 'matrix' in gltf_node:
                gltf_mat = LMatrix4(*gltf_node.get('matrix'))
            else:
                gltf_mat = LMatrix4(LMatrix4.ident_mat())
                if 'scale' in gltf_node:
                    gltf_mat.set_scale_mat(tuple(gltf_node['scale']))

                if 'rotation' in gltf_node:
                    rot_mat = LMatrix4()
                    rot = gltf_node['rotation']
                    quat = LQuaternion(rot[3], rot[0], rot[1], rot[2])
                    quat.extract_to_matrix(rot_mat)
                    gltf_mat *= rot_mat

                if 'translation' in gltf_node:
                    gltf_mat *= LMatrix4.translate_mat(*gltf_node['translation'])

            panda_node.set_transform(TransformState.make_mat(self.csxform_inv * gltf_mat * self.csxform))

            np = self.node_paths.get(nodeid, root.attach_new_node(panda_node))
            self.node_paths[nodeid] = np

            if nodeid in self.skeletons:
                # self.build_character(panda_node, nodeid, jvtmap, cvsmap, gltf_data)
                # wrap root bone in armature
                char = ArmatureNode(node_name)
                np.reparent_to(root.attach_new_node(char))

            if 'hidden_nodes' in scene_extras:
                if nodeid in scene_extras['hidden_nodes']:
                    panda_node = panda_node.make_copy()

            if 'mesh' in gltf_node:
                meshid = gltf_node['mesh']
                gltf_mesh = gltf_data['meshes'][meshid]
                mesh = self.meshes[meshid]

                # Does this mesh have weights, but are we not under a character?
                # If so, create a character just for this mesh.
                # if gltf_mesh.get('weights') and not jvtmap and not cvsmap:
                #     mesh_name = gltf_mesh.get('name', 'mesh'+str(meshid))
                #     char = Character(mesh_name)
                #     cvsmap2 = {}
                #     self.build_character(char, nodeid, {}, cvsmap2, gltf_data, recurse=False)
                #     self.combine_mesh_morphs(mesh, meshid, cvsmap2)

                #     np.attach_new_node(char).attach_new_node(mesh)
                # else:
                if True:
                    np.attach_new_node(mesh)
                    if jvtmap:
                        self.combine_mesh_skin(mesh, jvtmap)
                    if cvsmap:
                        self.combine_mesh_morphs(mesh, meshid, cvsmap)

                    if 'skin' in gltf_node:
                        skinid = gltf_node['skin']
                        gltf_skin = gltf_data['skins'][skinid]
                        if 'skeleton' in gltf_skin:
                            skeletonid = gltf_skin['skeleton']
                            self._mesh2joint[nodeid] = skeletonid
                        else:
                            for skeletonid, skinid2 in self.skeletons.items():
                                if skinid == skinid2:
                                    self._mesh2joint[nodeid] = skeletonid
                                    break

            if 'camera' in gltf_node:
                camid = gltf_node['camera']
                cam = self.cameras[camid]
                np.attach_new_node(cam)
            if 'extensions' in gltf_node:
                light_ext = None
                has_light_ext = False
                if 'KHR_lights_punctual' in gltf_node['extensions']:
                    light_ext = 'KHR_lights_punctual'
                    has_light_ext = True
                elif 'KHR_lights' in gltf_node['extensions']:
                    light_ext = 'KHR_lights'
                    has_light_ext = True
                if has_light_ext:
                    lightid = gltf_node['extensions'][light_ext]['light']
                    light = self.lights[lightid]
                    lnp = np.attach_new_node(light)
                    if self.compose_cs == CS_zup_right:
                        lnp.set_p(lnp.get_p() - 90)
                    lnp.set_r(lnp.get_r() - 90)
                    if isinstance(light, Light):
                        root.set_light(lnp)

                has_physics = (
                    'BLENDER_physics' in gltf_node['extensions'] or
                    'PANDA3D_physics_collision_shapes' in gltf_node['extensions']
                )
                if has_physics:
                    gltf_collisions = gltf_node['extensions'].get(
                        'PANDA3D_physics_collision_shapes',
                        gltf_node['extensions']['BLENDER_physics']
                    )
                    gltf_rigidbody = gltf_node['extensions'].get('BLENDER_physics', None)
                    if 'PANDA3D_physics_collision_shapes' in gltf_node['extensions']:
                        collision_shape = gltf_collisions['shapes'][0]
                        shape_type = collision_shape['type']
                    else:
                        collision_shape = gltf_collisions['collisionShapes'][0]
                        shape_type = collision_shape['shapeType']
                    bounding_box = collision_shape['boundingBox']
                    radius = max(bounding_box[0], bounding_box[1]) / 2.0
                    height = bounding_box[2]
                    geomnode = None
                    intangible = gltf_collisions.get('intangible', False)
                    if 'mesh' in collision_shape:
                        try:
                            geomnode = self.meshes[collision_shape['mesh']]
                        except KeyError:
                            print(
                                "Could not find physics mesh ({}) for object ({})"
                                .format(collision_shape['mesh'], nodeid)
                            )
                    if 'extensions' in gltf_data and 'BP_physics_engine' in gltf_data['extensions']:
                        use_bullet = (
                            gltf_data['extensions']['BP_physics_engine']['engine'] == 'bullet'
                        )
                    else:
                        use_bullet = self.settings.collision_shapes == 'bullet'
                    if use_bullet and not HAVE_BULLET:
                        print(
                            'Warning: attempted to export for Bullet, which is unavailable, falling back to builtin'
                        )
                        use_bullet = False

                    if use_bullet:
                        phynode = self.load_physics_bullet(
                            node_name,
                            geomnode,
                            shape_type,
                            bounding_box,
                            radius,
                            height,
                            intangible,
                            gltf_rigidbody
                        )
                    else:
                        phynode = self.load_physics_builtin(
                            node_name,
                            geomnode,
                            shape_type,
                            bounding_box,
                            radius,
                            height,
                            intangible
                        )
                    if phynode is not None:
                        phynp = np.attach_new_node(phynode)
                        for geomnode in np.find_all_matches('+GeomNode'):
                            geomnode.reparent_to(phynp)

            for key, value in get_extras(gltf_node).items():
                np.set_tag(key, str(value))

            for child_nodeid in gltf_node.get('children', []):
                add_node(np, gltf_scene, child_nodeid, jvtmap, cvsmap)

            # Handle visibility after children are loaded
            def visible_recursive(node, visible):
                if visible:
                    node.show()
                else:
                    node.hide()
                for child in node.get_children():
                    visible_recursive(child, visible)

            hidden_nodes = scene_extras.get('hidden_nodes', [])
            if nodeid in hidden_nodes:
                #print('Hiding', np)
                visible_recursive(np, False)
            else:
                #print('Showing', np)
                visible_recursive(np, True)

            # Check if we need to deal with negative scale values
            scale = panda_node.get_transform().get_scale()
            negscale = scale.x * scale.y * scale.z < 0
            if negscale:
                for geomnode in np.find_all_matches('**/+GeomNode'):
                    tmp = geomnode.get_parent().attach_new_node(PandaNode('ReverseCulling'))
                    tmp.set_attrib(CullFaceAttrib.make_reverse())
                    geomnode.reparent_to(tmp)

            # Handle parenting to joints
            joint = self.joint_parents.get(nodeid)
            if joint:
                xformnp = root.attach_new_node(PandaNode('{}-parent'.format(node_name)))
                np.reparent_to(xformnp)
                joint.add_net_transform(xformnp.node())

        for sceneid, gltf_scene in enumerate(gltf_data.get('scenes', [])):
            scene_name = gltf_scene.get('name', 'scene'+str(sceneid))
            scene_root = NodePath(ModelRoot(scene_name))

            node_list = gltf_scene['nodes']
            hidden_nodes = get_extras(gltf_scene).get('hidden_nodes', [])
            node_list += hidden_nodes

            for nodeid in node_list:
                add_node(scene_root, gltf_scene, nodeid, {}, {})

            if self.settings.flatten_nodes:
                scene_root.flatten_medium()

            self.scenes[sceneid] = scene_root

        # Set the active scene
        sceneid = gltf_data.get('scene', 0)
        if sceneid in self.scenes:
            self.active_scene = self.scenes[sceneid]
        if 'scenes' in gltf_data:
            gltf_scene = gltf_data['scenes'][sceneid]
            scene_extras = get_extras(gltf_scene)
            if 'background_color' in scene_extras:
                self.background_color = scene_extras['background_color']
            if 'active_camera' in scene_extras:
                self.active_camera = scene_extras['active_camera']

        # move geom nodes to skeleton bones
        for mesh_nodeid, joint_nodeid in self._mesh2joint.items():
            mesh = self.node_paths[mesh_nodeid]
            bone = self.node_paths[joint_nodeid]
            # search for the armature
            armature = bone
            while armature.has_parent() and armature.node().get_class_type().get_name() != 'ArmatureNode':
                armature = armature.get_parent()
            # reparent with saving transforms
            t = mesh.get_transform(armature)
            mesh.reparent_to(armature)
            mesh.set_transform(t)


def is_glb_file(filepath):
    return filepath.endswith('.glb')


def parse_gltf_file(filepath):
    data = None

    if is_glb_file(filepath):
        with dopen(filepath, 'rb') as glbfile:
            data = parse_glb_data(glbfile)

    else:
        with dopen(filepath, 'r') as gltffile:
            data = parse_gltf_data(gltffile)

    return data


def load_actor(file_path=None, gltf_data=None, gltf_settings=None, converter_class=None):
    if converter_class is None:
        converter_class = KPhysConverter

    converter = converter_class(file_path, settings=gltf_settings)
    if gltf_data is None:
        gltf_data = parse_gltf_file(file_path)
    converter.update(gltf_data)
    return converter.active_scene.node()
