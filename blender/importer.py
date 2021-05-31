import os

import bmesh
import bpy
from bmesh.types import BMesh
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from mathutils import Matrix, Vector

from ..xfbin_lib.xfbin.structure.nucc import (CoordNode, NuccChunkClump,
                                              NuccChunkModel)
from ..xfbin_lib.xfbin.structure.nud import NudMesh
from ..xfbin_lib.xfbin.structure.xfbin import Xfbin
from ..xfbin_lib.xfbin.xfbin_reader import read_xfbin
from .common.coordinate_converter import *


class ImportXFBIN(Operator, ImportHelper):
    """Loads an XFBIN file into blender"""
    bl_idname = "import_scene.xfbin"
    bl_label = "Import XFBIN"

    use_full_material_names: BoolProperty(
        name="Full material names",
        description="Display full name of materials in NUD meshes, instead of a shortened form")

    filter_glob: StringProperty(default="*.xfbin", options={"HIDDEN"})

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.prop(self, 'use_full_material_names')

    def execute(self, context):
        import time

        # try:
        start_time = time.time()
        importer = XfbinImporter(self.filepath, self.as_keywords(ignore=("filter_glob",)))

        importer.read(context)

        elapsed_s = "{:.2f}s".format(time.time() - start_time)
        print("XFBIN import finished in " + elapsed_s)

        return {'FINISHED'}
        # except Exception as error:
        #     print("Catching Error")
        #     self.report({"ERROR"}, str(error))
        # return {'CANCELLED'}


class XfbinImporter:
    def __init__(self, filepath, import_settings):
        self.filepath = filepath
        self.use_full_material_names = import_settings.get("use_full_material_names")

    xfbin: Xfbin
    collection: bpy.types.Collection

    def read(self, context):
        self.xfbin = read_xfbin(self.filepath)
        self.collection = self.make_collection(context)

        for page in self.xfbin.pages:
            clump = page.get_chunks_by_type('nuccChunkClump')

            if not len(clump):
                continue

            clump: NuccChunkClump = clump[0]

            armature_obj = self.make_armature(clump, context)
            self.make_objects(clump, armature_obj, context)
            bpy.ops.object.mode_set(mode='OBJECT')

    def make_collection(self, context) -> bpy.types.Collection:
        """
        Build a collection to hold all of the objects and meshes from the GMDScene.
        :param context: The context used by the import process.
        :return: A collection which the importer can add objects and meshes to.
        """

        collection_name = os.path.basename(self.filepath).split('.')[0]
        collection = bpy.data.collections.new(collection_name)
        # Link the new collection to the currently active collection.
        context.collection.children.link(collection)
        return collection

    def make_armature(self, clump: NuccChunkClump, context):
        armature_name = clump.name

        armature = bpy.data.armatures.new(f"{armature_name}")
        armature.display_type = 'STICK'

        armature_obj = bpy.data.objects.new(f"{armature_name}", armature)
        armature_obj.show_in_front = True

        self.collection.objects.link(armature_obj)

        context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')

        bone_matrices = dict()

        def generate_perpendicular_bone_direction(this_bone_matrix: Matrix, parent_dir: Vector):
            # Pick a vector that's sort of in the same direction we want the bone to point in
            # (i.e. we don't want the bone to go in/out, so don't pick (0, 0, 1))
            target_dir = Vector((0, 1, 0))
            if abs(parent_dir.dot(target_dir)) > 0.99:
                # Parent and proposed perpendicular direction are basically the same axis, cross product won't work
                # Choose a different one
                target_dir = Vector((1, 0, 0))

            # parent_dir cross target_dir creates a vector that's guaranteed to be perpendicular to both of them.
            perp_dir = parent_dir.cross(target_dir).normalized()
            print(f"{parent_dir} X {target_dir} = {perp_dir}")

            # Then, parent_dir cross perp_dir will create a vector that is both
            #   1) perpendicular to parent_dir
            #   2) in the same sort of direction as target_dir
            # use this vector as our tail_delta
            tail_delta_dir = parent_dir.cross(perp_dir).normalized()
            print(f"{parent_dir} X {perp_dir} = {tail_delta_dir}")

            # Cross product can have bad symmetry - bones on opposite sides of the skeleton can get deltas that look weird
            # Fix this by picking the delta which moves the tail the farthest possible distance from the origin
            # This will choose consistent directions regardless of which side of the vertical axis you are on
            distance_from_origin_with_positive = (this_bone_matrix @ (tail_delta_dir * 0.1)).length
            distance_from_origin_with_negative = (this_bone_matrix @ (-tail_delta_dir * 0.1)).length
            if distance_from_origin_with_negative > distance_from_origin_with_positive:
                tail_delta_dir = -tail_delta_dir

            return tail_delta_dir

        def make_bone(node: CoordNode):

            # Find the local->world matrix for the parent bone, and use this to find the local->world matrix for the current bone
            if node.parent:
                parent_matrix = bone_matrices[node.parent.name]
            else:
                parent_matrix = Matrix.Identity(4)

            pos = pos_cm_to_m(node.position)
            rot = rot_to_blender(node.rotation)

            print(f"bone {node.name}")
            print(f"Actual Data\n{pos},    {rot},    {node.scale}")
            print()

            this_bone_matrix = rot.to_matrix().to_4x4()
            this_bone_matrix.invert()
            this_bone_matrix = this_bone_matrix @ Matrix.Diagonal(Vector(node.scale).xyz).to_4x4()
            this_bone_matrix = parent_matrix @ (Matrix.Translation(Vector(pos).xyz) @ this_bone_matrix)

            # Remove scale from matrix before inserting into the dictionary
            # TODO: Should bones really have scale, or is it only used for setting up the skeleton? Needs in-game testing
            bone_matrices[node.name] = this_bone_matrix @ Matrix.Diagonal(Vector(node.scale).xyz).to_4x4().inverted()

            # # Take a page out of XNA Importer's book for bone tails - make roots just stick towards the camera
            # # and make nodes with (non-twist) children try to go to the average of those children's positions
            # if not node.parent:
            #     tail_delta = Vector((0, 0, 0.5))
            # else:
            #     # This either isn't a twist bone or it has children - most likely this just isn't a twist bone, as twist bones generally don't have children anyway
            #     # If there are non-twist children, set the tail to the average of their positions
            #     countable_children_gmd_positions = [pos_scale_to_blender(child.position) for child in node.children]

            #     if countable_children_gmd_positions:
            #         # TODO - if children all start at the same place we do, tail_delta = (0,0,0) and bone disappears
            #         #  Do the perpendicular thing for this case too? Requires refactor
            #         tail_delta = sum(countable_children_gmd_positions, Vector((0,0,0))) / len(countable_children_gmd_positions)

            #         if tail_delta.length < 0.001:
            #             if pos.xyz.length < 0.00001:
            #                 tail_delta = Vector((0, 0, 0.05))
            #             else:
            #                 parent_dir = pos.xyz.normalized()  # pos is relative to the parent already
            #                 tail_delta_dir = generate_perpendicular_bone_direction(this_bone_matrix, parent_dir)
            #                 tail_delta = (tail_delta_dir.xyz * 0.1)
            #     else:
            #         # Extend the tail in the direction of the parent
            #         # pos.xyz is relative to the parent already
            #         if pos.xyz.length < 0.00001:
            #             tail_delta = Vector((0, 0, 0.05))
            #         else:
            #             tail_delta = pos.xyz.normalized() * 0.05

            bone = armature.edit_bones.new(node.name)
            bone.use_relative_parent = False
            bone.inherit_scale = 'NONE'  # TODO: is this correct?
            bone.use_deform = True

            print(f"Matrix \n{this_bone_matrix}")
            print()
            print(
                f"Matrix Decomposed \n{this_bone_matrix.to_translation()},    {this_bone_matrix.to_euler()},    {this_bone_matrix.to_scale()}")
            print()
            print()
            print()

            bone.head = this_bone_matrix @ Vector((0, 0, 0))

            # Having a long tail would offset the meshes parented to the mesh bones, so we avoid that for now
            bone.tail = this_bone_matrix @ Vector((0, 0, 0.0001))

            # if tail_delta.length < 0.00001:
            #     self.error.recoverable(f"Bone {bone.name} generated a tail_delta of 0 and will be deleted by Blender.")

            if node.parent:
                bone.parent = armature.edit_bones[node.parent.name]
                # If your head is close to your parent's tail, turn on "connected to parent"
                #bone.use_connect = (bone.head - bone.parent.tail).length < 0.001
            else:
                bone.parent = None

            for child in node.children:
                make_bone(child)

        for root in clump.root_nodes:
            make_bone(root)

        return armature_obj

    def make_objects(self, clump: NuccChunkClump, armature_obj, context):
        vertex_group_list = [coord.node.name for coord in clump.coord_chunks]
        vertex_group_indices = {
            name: i
            for i, name in enumerate(vertex_group_list)
        }

        # Small QoL fix for JoJo "_f" models to show shortened material names
        clump_name = clump.name
        if clump_name.endswith('_f'):
            clump_name = clump_name[:-2]

        for nucc_model in clump.model_chunks:
            if not (isinstance(nucc_model, NuccChunkModel) and nucc_model.nud):
                continue

            nud = nucc_model.nud

            for group in nud.mesh_groups:
                for i, mesh in enumerate(group.meshes):
                    mat_name = nucc_model.material_chunks[i].name

                    # Try to shorten the material name before adding it to the mesh name
                    if (not self.use_full_material_names) and mat_name.startswith(clump_name):
                        mat_name = mat_name[len(clump_name):].strip(' _')

                    # Add the material name to the group name because we don't have a way
                    # to differentiate between meshes in the same group
                    mesh_name = f'{group.name} [{mat_name}]' if len(mat_name) else group.name

                    overall_mesh = bpy.data.meshes.new(mesh_name)

                    # This list will get filled in nud_mesh_to_bmesh
                    custom_normals = list()
                    new_bmesh = self.nud_mesh_to_bmesh(mesh, clump, vertex_group_indices, custom_normals)

                    # Convert BMesh to blender Mesh
                    new_bmesh.to_mesh(overall_mesh)
                    new_bmesh.free()

                    # Use the custom normals we made eariler
                    overall_mesh.create_normals_split()
                    overall_mesh.normals_split_custom_set_from_vertices(custom_normals)
                    overall_mesh.auto_smooth_angle = 0
                    overall_mesh.use_auto_smooth = True

                    mesh_obj: bpy.types.Object = bpy.data.objects.new(mesh_name, overall_mesh)

                    # Parent the mesh to the armature
                    mesh_obj.parent = armature_obj

                    # Set the mesh bone as the mesh's parent bone, if it exists (it should)
                    if armature_obj.data.edit_bones.get(group.name, None):
                        mesh_obj.parent_bone = group.name
                        mesh_obj.parent_type = 'BONE'

                    # Create the vertex groups (should change this to create *only* the needed groups)
                    for name in [coord.node.name for coord in clump.coord_chunks]:
                        mesh_obj.vertex_groups.new(name=name)

                    # Apply the armature modifier
                    modifier = mesh_obj.modifiers.new(type='ARMATURE', name="Armature")
                    modifier.object = armature_obj

                    # Link the mesh object to the collection
                    self.collection.objects.link(mesh_obj)

        # for nucc_model in clump.model_chunks:
        #     if not (isinstance(nucc_model, NuccChunkModel) and nucc_model.nud):
        #         continue

        #     nud = nucc_model.nud

        #     for group in nud.mesh_groups:
        #         for i in range(len(group.meshes)):
        #             mesh_name = f'{nucc_model.name} ({nucc_model.material_chunks[i].name})'
        #             overall_mesh = bpy.data.meshes.new(mesh_name)

        #             overall_mesh.from_pydata(self.make_vertices(group.meshes[i].vertices), [], group.meshes[i].faces)
        #             overall_mesh.update(calc_edges=True)

        #             mesh_obj: bpy.types.Object = bpy.data.objects.new(mesh_name, overall_mesh)
        #             mesh_obj.location = (0, 0, 0)

        #             # Set the mesh bone as the mesh's parent
        #             if armature_obj.data.edit_bones.get(group.name, None):
        #                 mesh_obj.parent = armature_obj
        #                 mesh_obj.parent_bone = group.name
        #                 mesh_obj.parent_type = 'BONE'

        #             self.collection.objects.link(mesh_obj)

    def nud_mesh_to_bmesh(self, mesh: NudMesh, clump: NuccChunkClump, vertex_group_indices, custom_normals) -> BMesh:
        bm = bmesh.new()

        deform = bm.verts.layers.deform.new("Vertex Weights")

        # Vertices
        for i in range(len(mesh.vertices)):
            vtx = mesh.vertices[i]
            vert = bm.verts.new(pos_scale_to_blender(vtx.position))

            # Tangents cannot be applied
            if vtx.normal:
                normal = pos_to_blender(vtx.normal)
                custom_normals.append(normal)
                vert.normal = normal

            if vtx.bone_weights:
                for bone_id, bone_weight in zip(vtx.bone_ids, vtx.bone_weights):
                    if bone_weight > 0:
                        vertex_group_index = vertex_group_indices[clump.coord_chunks[bone_id].name]
                        vert[deform][vertex_group_index] = bone_weight

        # Set up the indexing table inside the bmesh so lookups work
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()

        # For each triangle, add it to the bmesh
        for mesh_face in mesh.faces:
            tri_idxs = mesh_face

            # Skip "degenerate" triangles
            if len(set(tri_idxs)) != 3:
                continue

            if -1 in tri_idxs:
                print(f"Found a negative index inside a triangle_indices list! That shouldn't happen.")
                continue

            try:
                face = bm.faces.new((bm.verts[tri_idxs[0]], bm.verts[tri_idxs[1]], bm.verts[tri_idxs[2]]))
                face.smooth = True

                # TODO: materials
                #face.material_index = material_index
            except Exception as e:
                # We might get duplicate faces for some reason
                # print(e)
                pass

        # Color
        if len(mesh.vertices) and mesh.vertices[0].color:
            col_layer = bm.loops.layers.color.new("Color")
            for face in bm.faces:
                for loop in face.loops:
                    color = mesh.vertices[loop.vert.index].color
                    loop[col_layer] = (color[0], color[1], color[2], color[3])

        # # UVs
        # if len(mesh.vertices) and mesh.vertices[0].uv:
        #     for i, uv in enumerate(list(map(lambda x: x.uv, mesh.vertices))):
        #         uv_layer = bm.loops.layers.uv.new(f"UV_Primary")
        #         for face in bm.faces:
        #             for loop in face.loops:
        #                 original_uv = uv[0]
        #                 loop[uv_layer].uv = (original_uv[0], 1.0 - original_uv[1])

        return bm

    def make_vertices(self, mesh_vertices):
        return list(map(lambda x: pos_scale_to_blender(x.position), mesh_vertices))


def menu_func_import(self, context):
    self.layout.operator(ImportXFBIN.bl_idname, text='CyberConnect2 model container (.xfbin)')
