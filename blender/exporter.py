from functools import reduce
from os import path
from typing import Dict, List

import bmesh
import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Armature, EditBone, Mesh, Object, Operator
from bpy_extras.io_utils import ExportHelper
from mathutils import Matrix, Quaternion, Vector

from ..xfbin_lib.xfbin.structure.nucc import (CoordNode, NuccChunkClump,
                                              NuccChunkCoord,
                                              NuccChunkMaterial,
                                              NuccChunkModel, RiggingFlag)
from ..xfbin_lib.xfbin.structure.nud import (Nud, NudMaterial, NudMesh,
                                             NudMeshGroup, NudVertex)
from ..xfbin_lib.xfbin.structure.xfbin import Xfbin
from ..xfbin_lib.xfbin.xfbin_reader import read_xfbin
from ..xfbin_lib.xfbin.xfbin_writer import write_xfbin_to_path
from .common.coordinate_converter import *
from .panels.clump_panel import XfbinMaterialPropertyGroup
from .common.helpers import hex_str_to_int, int_to_hex_str
from .panels.nud_mesh_panel import NudMeshPropertyGroup


class ExportXfbin(Operator, ExportHelper):
    """Export current collection as XFBIN file"""
    bl_idname = 'export_scene.xfbin'
    bl_label = 'Export XFBIN'

    filename_ext = ''

    filter_glob: StringProperty(default='*.xfbin', options={'HIDDEN'})

    def collection_callback(self, context):
        items = set()
        active_col = bpy.context.collection

        if active_col:
            items.add((active_col.name, active_col.name, ''))

        items.update([(c.name, c.name, '') for c in bpy.data.collections])

        return list(items)

    collection: EnumProperty(
        items=collection_callback,
        name='Collection to Export',
        description='The collection to be exported. All armatures in the collection will be converted and put in the same XFBIN',
    )

    inject_to_xfbin: BoolProperty(
        name='Inject to existing XFBIN',
        description='If True, will add (or overwrite) the exportable models as pages in the selected XFBIN.\n'
        'If False, will create a new XFBIN and overwrite the old file if it exists.\n\n'
        'NOTE: If True, the selected path has to be an XFBIN file that already exists, and that file will be overwritten',
        default=True,
    )

    export_meshes: BoolProperty(
        name='Export meshes',
        description='If True, will export the meshes of each armature in the collection to the XFBIN.\n'
        'If False, will NOT rebuild the meshes nor update the ones in the XFBIN.\n\n'
        'NOTE: "Inject to existing XFBIN" has to be enabled for this option to take effect',
        default=True,
    )

    export_bones: BoolProperty(
        name='Export bones',
        description='If True, will export the bones of each armature in the collection to the XFBIN.\n'
        'If False, will NOT update the bone coordinates in the XFBIN.\n\n'
        'NOTE: "Inject to existing XFBIN" has to be enabled for this option to take effect',
        default=False,
    )

    export_materials: BoolProperty(
        name='Export materials',
        description='If True, will export the materials in the collection to the XFBIN.\n'
        'If False, will NOT update the materials of each clump in the XFBIN.\n\n'
        'NOTE: "Inject to existing XFBIN" has to be enabled for this option to take effect',
        default=False,
    )

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = True  # No animation.

        layout.prop(self, 'collection')

        # TODO: Re-enable changing these when support is added
        inject_row = layout.row()
        inject_row.prop(self, 'inject_to_xfbin')
        inject_row.enabled = False

        layout.prop(self, 'export_meshes')

        bone_row = layout.row()
        bone_row.prop(self, 'export_bones')
        bone_row.enabled = False

        mat_row = layout.row()
        mat_row.prop(self, 'export_materials')
        mat_row.enabled = False

    def execute(self, context):
        # try:
        exporter = XfbinExporter(self.filepath, self.as_keywords(ignore=('filter_glob',)))
        exporter.export_collection(context)

        self.report({'INFO'}, f'Finished exporting {exporter.collection.name}')
        return {'FINISHED'}
        # except Exception as e:
        #     print(e)
        #     self.report({'ERROR'}, str(e))
        # return {'CANCELLED'}


class XfbinExporter:
    def __init__(self, filepath, import_settings: dict):
        self.filepath = filepath
        self.collection: bpy.types.Collection = bpy.data.collections[import_settings.get('collection')]

        self.inject_to_xfbin = import_settings.get('inject_to_xfbin')

        self.export_meshes = import_settings.get('export_meshes')
        self.export_bones = import_settings.get('export_bones')
        self.export_materials = import_settings.get('export_materials')

    xfbin: Xfbin

    def export_collection(self, context):
        self.xfbin = Xfbin()
        if self.inject_to_xfbin:
            if not path.isfile(self.filepath):
                raise Exception(f'Cannot inject XFBIN - File does not exist: {self.filepath}')

            self.xfbin = read_xfbin(self.filepath)
        else:
            self.export_meshes = self.export_bones = self.export_materials = True

        for armature_obj in [obj for obj in self.collection.objects if obj.type == 'ARMATURE']:
            self.xfbin.add_clump_page(self.make_clump(armature_obj, context))

        # Write the xfbin
        write_xfbin_to_path(self.xfbin, self.filepath)

    def make_clump(self, armature_obj: Object, context) -> NuccChunkClump:
        """Creates and returns a NuccChunkClump made from an Armature and its child meshes."""

        armature: Armature = armature_obj.data
        empties: List[Mesh] = [obj for obj in armature_obj.children if obj.type == 'EMPTY']

        clump = NuccChunkClump(armature_obj.xfbin_clump_data.path, armature.name)
        old_clump = None

        if self.inject_to_xfbin:
            # Try to get the clump in the existing xfbin
            old_clump = self.xfbin.get_chunk_page(clump)

            if old_clump:
                # There should be only 1 clump per page anyway
                old_clump = old_clump[1].get_chunks_by_type(NuccChunkClump)[0]

        if self.export_bones:
            clump.coord_chunks = self.make_coords(armature, clump, context)
        elif old_clump:
            clump.coord_chunks = old_clump.coord_chunks
        else:
            raise Exception('Cannot export bones.')

        if self.export_meshes:
            # Create the material chunks
            xfbin_mats = dict()
            for mat in armature_obj.xfbin_clump_data.materials:
                xfbin_mats[mat.material_name] = self.make_xfbin_material(mat, clump, context)

            # Create the model chunks
            clump.model_chunks = self.make_models(empties, clump, old_clump, xfbin_mats, context)

            # TODO: Add support for adding new model groups (from xfbin_clump_data)
            clump.model_groups = [list(clump.model_chunks)]
        elif old_clump:
            clump.model_chunks = old_clump.model_chunks
            clump.model_groups = old_clump.model_groups
        else:
            raise Exception('Cannot export meshes.')

        return clump

    def make_coords(self, armature: Armature, clump: NuccChunkClump, context) -> List[NuccChunkCoord]:
        bpy.ops.object.mode_set(mode='EDIT')

        coords: List[NuccChunkCoord] = list()

        def make_coord(bone: EditBone, coord_parent: CoordNode = None, parent_matrix: Matrix = Matrix.Identity(4)) -> NuccChunkCoord:
            coord = NuccChunkCoord(clump.filePath, bone.name)
            coord.node = CoordNode(coord)

            # Set up the node
            node = coord.node
            node.parent = coord_parent

            # Set the coordinates of the node
            # TODO: Properly convert the coordinates
            node.position = pos_m_to_cm((parent_matrix.inverted() @ bone.matrix).to_translation())
            node.rotation = rot_from_blender((parent_matrix.inverted() @ bone.matrix).to_euler())
            node.scale = pos_from_blender((parent_matrix.inverted() @ bone.matrix).to_scale())

            node.unkFloat = 1.0
            node.unkShort = 0

            # Add the coord chunk to the list
            coords.append(coord)

            # Recursively add all children of each bone
            for c in bone.children:
                make_coord(c, node, bone.matrix)

        # Iterate through the root bones to process their children in order
        for root_bone in [b for b in armature.edit_bones if b.parent is None]:
            make_coord(root_bone)

        for coord in coords:
            if coord.node.parent:
                coord.node.parent.children.append(coord.node)

        bpy.ops.object.mode_set(mode='OBJECT')

        return coords

    def make_models(self, empties: List[Object], clump: NuccChunkClump, old_clump: NuccChunkClump, xfbin_mats: Dict[str, NuccChunkMaterial], context) -> List[NuccChunkModel]:
        model_chunks = list()

        coord_indices_dict = {
            name: i
            for i, name in enumerate(tuple(map(lambda c: c.name, clump.coord_chunks)))
        }

        for empty in empties:
            # Create the chunk and set its properties
            chunk = NuccChunkModel(clump.filePath, empty.name)
            chunk.clump_chunk = clump

            # Get the index of the mesh bone of this model
            chunk.coord_index = coord_indices_dict.get(empty.xfbin_nud_data.mesh_bone, 0)

            chunk.material_chunks = list()

            # Reduce the set of flags to a single flag
            chunk.rigging_flag = RiggingFlag(reduce(lambda x, y: int(x) |
                                                    int(y), empty.xfbin_nud_data.rigging_flag.union(empty.xfbin_nud_data.rigging_flag_extra), 0))

            chunk.material_flags = list(empty.xfbin_nud_data.material_flags)
            chunk.flag1_floats = list(
                empty.xfbin_nud_data.flag1_floats) if empty.xfbin_nud_data.material_flags[1] & 0x04 else tuple()

            # Create the nud
            chunk.nud = Nud()
            chunk.nud.name = chunk.name

            # Always treat nuds as having only 1 mesh group
            chunk.nud.mesh_groups = [NudMeshGroup()]
            mesh_group = chunk.nud.mesh_groups[0]
            mesh_group.name = chunk.name
            mesh_group.meshes = list()

            for mesh_obj in [c for c in empty.children if c.type == 'MESH']:
                nud_mesh = NudMesh()
                vertices = nud_mesh.vertices = list()
                faces = nud_mesh.faces = list()

                # Generate a mesh with modifiers applied, and put it into a bmesh
                mesh = mesh_obj.evaluated_get(context.evaluated_depsgraph_get()).data

                bm = bmesh.new()
                bm.from_mesh(mesh)
                bm.verts.ensure_lookup_table()
                bm.verts.index_update()

                # Get the current bone weighting layer
                deform_layer = bm.verts.layers.deform.active
                v_groups = mesh_obj.vertex_groups

                color_layer = None
                if len(bm.loops.layers.color):
                    color_layer = bm.loops.layers.color[0]

                uv_layer1 = None
                uv_layer2 = None
                if len(bm.loops.layers.uv):
                    uv_layer1 = bm.loops.layers.uv[0]
                if len(bm.loops.layers.uv) > 1:
                    uv_layer2 = bm.loops.layers.uv[1]

                # Loop vertex index -> nud vertex index
                vertex_indices_dict = dict()

                for tri_loops in bm.calc_loop_triangles():
                    for l in tri_loops:
                        # TODO: Check for non-smooth loops
                        if l.vert.index not in vertex_indices_dict:
                            # Add this index as a key to the dictionary
                            vertex_indices_dict[l.vert.index] = len(vertex_indices_dict)

                            # Create and add the vertex
                            vert = NudVertex()
                            vertices.append(vert)

                            # Position and normal, tangent, bitangent
                            vert.position = pos_scaled_from_blender(l.vert.co.xyz)
                            vert.normal = pos_from_blender(l.calc_normal().xyz)  # l.vert.normal.xyz
                            vert.tangent = pos_from_blender(l.calc_tangent().xyz)
                            vert.bitangent = Vector(vert.normal).cross(Vector(vert.tangent))

                            # Color
                            vert.color = l[color_layer].xyzw

                            # UV
                            vert.uv = list()
                            if uv_layer1:
                                vert.uv.append(uv_from_blender(l[uv_layer1].uv))
                            if uv_layer2:
                                vert.uv.append(uv_from_blender(l[uv_layer2].uv))

                            # Bone indices and weights
                            # Direct copy of TheTurboTurnip's weight sorting method
                            # https://github.com/theturboturnip/yk_gmd_io/blob/master/yk_gmd_blender/blender/export/legacy/exporter.py#L302-L316

                            # Get a list of (vertex group ID, weight) items sorted in descending order of weight
                            # Take the top 4 elements, for the top 4 most deforming bones
                            # Normalize the weights so they sum to 1
                            b_weights = [(v_groups[b].name, w) for b, w in sorted(l.vert[deform_layer].items(),
                                                                                  key=lambda i: 1 - i[1]) if v_groups[b].name in coord_indices_dict]
                            if len(b_weights) > 4:
                                b_weights = b_weights[:4]
                            elif len(b_weights) < 4:
                                # Add zeroed elements to b_weights so it's 4 elements long
                                b_weights += [(0, 0.0)] * (4 - len(b_weights))

                            weight_sum = sum(weight for (_, weight) in b_weights)
                            if weight_sum > 0.0:
                                vert.bone_ids = tuple(map(lambda bw: coord_indices_dict.get(bw[0], 0), b_weights))
                                vert.bone_weights = tuple(map(lambda bw: bw[1] / weight_sum, b_weights))
                            else:
                                vert.bone_ids = [0] * 4
                                vert.bone_weights = [0] * 3 + [1]

                    # Get the vertex indices to make the face
                    faces.append(tuple(map(lambda l: vertex_indices_dict[l.vert.index], tri_loops)))

                if len(vertices) < 3:
                    print(f'[NUD MESH] {mesh_obj.name} has no valid faces and will be skipped.')
                    continue

                if len(vertices) > NudMesh.MAX_VERTICES:
                    print(
                        f'[NUD MESH] {mesh_obj.name} has {len(vertices)} vertices (limit is {NudMesh.MAX_VERTICES}) and will be skipped.')
                    continue

                if len(faces) > NudMesh.MAX_FACES:
                    print(
                        f'[NUD MESH] {mesh_obj.name} has {len(bm.faces)} faces (limit is {NudMesh.MAX_FACES}) and will be skipped.')
                    continue

                # Only add the mesh if it doesn't exceed the vertex and face limits
                mesh_group.meshes.append(nud_mesh)

                # Free the mesh after we're done with it
                bm.free()

            if not mesh_group.meshes:
                print(f'[NUD] {empty.name} does not contain any exported meshes and will be skipped.')
                continue

            # Only add the model chunk if its NUD contains at least one mesh
            model_chunks.append(chunk)

        return model_chunks

    def make_xfbin_material(self, property_group: XfbinMaterialPropertyGroup, clump: NuccChunkClump, context) -> NuccChunkMaterial:
        chunk = NuccChunkMaterial(clump.filePath, property_group.material_name)

        chunk.field02 = property_group.field02
        chunk.field04 = property_group.field04

        chunk.format = hex_str_to_int(property_group.float_format)
        chunk.floats = list(property_group.floats)[:NuccChunkMaterial.float_count(chunk.format)]

        # TODO: Add texture groups

        return chunk


def menu_func_export(self, context):
    self.layout.operator(ExportXfbin.bl_idname, text='CyberConnect2 Model Container (.xfbin)')
