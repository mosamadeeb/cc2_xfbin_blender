from typing import List

import bpy
from bpy.props import (BoolProperty, CollectionProperty, IntProperty,
                       StringProperty)
from bpy.types import Panel, PropertyGroup

from ...xfbin_lib.xfbin.structure.nucc import NuccChunkTexture
from ..common.helpers import XFBIN_TEXTURES_OBJ
from .common import draw_xfbin_list
from ..common.shaders import F00A, _02_F00A, _05_F00D, _01_F003, _05_F002, _07_F002, _07_F010, _07_F00D, _01_F002, _01_F008, E002



# bpy.props don't support inheritance...
# So this is mostly a copy of XfbinNutTexturePropertyGroup
class XfbinTextureChunkPropertyGroup(PropertyGroup):
    def update_texture_name(self, context):
        self.update_name()

    texture_name: StringProperty(
        name='Texture Name',
        default='new_texture',
        update=update_texture_name,
    )

    path: StringProperty(
        name='Chunk Path',
        description='XFBIN chunk path that will be used for identifying the texture in the XFBIN.\n'
        'Should be the same as the path of the texture in the XFBIN to inject to.\n'
        'Example: "c/1nrt/tex/1nrtbody.nut"',
    )

    # TODO: Support exporting textures from blender
    # texture: StringProperty(
    #     name='Image Texture',
    # )

    def update_name(self):
        self.name = self.texture_name

    def init_data(self, chunk: NuccChunkTexture):
        self.texture_name = chunk.name
        self.path = chunk.filePath
        

    include: BoolProperty(
        name='Include in XFBIN',
        description='Repack the texture into the XFBIN when exporting.\n'
        'This should be enabled for all textures that are specific to the XFBIN '
        '(i.e. celshade/haching etc should not be included).\n\n'
        'Note: The path to the texture in NUT format (.nut) must be provided',
    )

    nut_path: StringProperty(
        name='NUT Path',
    )


class TextureChunksListPropertyGroup(PropertyGroup):
    texture_chunks: CollectionProperty(
        type=XfbinTextureChunkPropertyGroup,
    )

    texture_chunk_index: IntProperty()

    def init_data(self, texture_chunks: List[NuccChunkTexture]):
        self.texture_chunks.clear()
        for texture in texture_chunks:
            t: XfbinTextureChunkPropertyGroup = self.texture_chunks.add()
            t.init_data(texture)


class XFBIN_PANEL_OT_OpenNut(bpy.types.Operator):
    """Open a NUT texture to include in the XFBIN"""
    bl_idname = 'xfbin_panel.open_nut'
    bl_label = 'Open NUT (*.nut)'

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    filter_glob: StringProperty(default='*.nut', options={'HIDDEN'})

    def execute(self, context):
        data: TextureChunksListPropertyGroup = context.object.xfbin_texture_chunks_data
        chunks = data.texture_chunks
        index = data.texture_chunk_index

        if not chunks:
            # Should not happen
            return {'CANCELLED'}

        chunks[index].nut_path = self.filepath

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}


class XfbinTextureChunkPropertyPanel(Panel):
    bl_idname = 'OBJECT_PT_xfbin_texture_chunk_list'
    bl_label = '[XFBIN] Texture Chunks'

    bl_space_type = 'PROPERTIES'
    bl_context = 'object'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'EMPTY' and obj.parent is None and obj.name.startswith(XFBIN_TEXTURES_OBJ)

    def draw(self, context):
        layout = self.layout
        obj = context.object
        data: TextureChunksListPropertyGroup = obj.xfbin_texture_chunks_data

        layout.operator(RemakeShaders.bl_idname)

        draw_xfbin_list(layout, 0, data, f'xfbin_texture_chunks_data', 'texture_chunks', 'texture_chunk_index')
        index = data.texture_chunk_index

        if data.texture_chunks and index >= 0:
            texture_chunk: XfbinTextureChunkPropertyGroup = data.texture_chunks[index]
            box = layout.box()

            box.prop(texture_chunk, 'texture_name')
            box.prop(texture_chunk, 'path')

            box.prop(texture_chunk, 'include')

            if texture_chunk.include:
                # TODO: Select textures already loaded in blender instead of NUTs
                # box.prop_search(texture_chunk, 'texture', bpy.data, 'images')

                box.operator('xfbin_panel.open_nut', icon='FILEBROWSER')

                if texture_chunk.nut_path:
                    row = box.row()
                    row.prop(texture_chunk, 'nut_path')
                    row.enabled = False


class RemakeShaders(bpy.types.Operator):
    bl_idname = "object.remake_shaders"
    bl_label = "Remake Shaders"
    bl_description = 'Delete the current shaders and remake them, this is useful for when you import a texture file'
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'EMPTY' and obj.parent is None and obj.name.startswith(XFBIN_TEXTURES_OBJ)
    
    def execute(self, context):
        #Shader functions
        shaders_dict = {'00 00 F0 0A': F00A, '00 01 F0 0A': F00A, '00 02 F0 0A': _02_F00A, '00 05 F0 0D': _05_F00D,
        '00 01 F0 0D': _05_F00D, '00 01 F0 03': _01_F003, '00 05 F0 03': _01_F003, '00 05 F0 02': _05_F002, '00 07 F0 02':_07_F002,
        '00 00 E0 02': E002, '00 07 F0 10':_07_F010, '00 03 F0 10':_07_F010, '00 07 F0 0D':_07_F00D, '00 01 F0 02':_01_F002,
        '00 01 F0 08':_01_F008,}
        objects = [o for o in context.object.users_collection[0].objects if o.type == 'MESH']
        for o in objects:
            parent = o.parent.parent
            xfbin_mat = parent.xfbin_clump_data.materials[o.xfbin_mesh_data.xfbin_material]
            if f'[XFBIN] {xfbin_mat.name}' in bpy.data.materials:
                bpy.data.materials.remove(bpy.data.materials.get(f'[XFBIN] {xfbin_mat.name}'))


        for o in objects:
            parent = o.parent.parent
            if o.xfbin_mesh_data.materials[0].name in shaders_dict:
                xfbin_mat = parent.xfbin_clump_data.materials[o.xfbin_mesh_data.xfbin_material]
                if f'[XFBIN] {xfbin_mat.name}' not in bpy.data.materials:
                    material = shaders_dict.get(o.xfbin_mesh_data.materials[0].name)(self, xfbin_mat, f'[XFBIN] {xfbin_mat.name}', xfbin_mat.name)
                    o.material_slots[0].material = material
                else:
                    o.material_slots[0].material = bpy.data.materials[f'[XFBIN] {xfbin_mat.name}']
            else:
                xfbin_mat = parent.xfbin_clump_data.materials[o.xfbin_mesh_data.xfbin_material]

                material = bpy.data.materials.new(f'[XFBIN] {xfbin_mat.name}')
                material.use_nodes = True
                material.blend_method = 'CLIP'
                material.shadow_method = 'CLIP'

                #remove node groups with the same name to prevent issues with min and max values of some nodes
                if bpy.data.node_groups.get(xfbin_mat.name):
                    bpy.data.node_groups.remove(bpy.data.node_groups.get(xfbin_mat.name))
                

                if xfbin_mat.texture_groups and xfbin_mat.texture_groups[0].textures:
                    #texcount = len(xfbin_mat.texture_groups[0].textures)
                    not_included = ['celshade', 'haching', 'haching1', 'haching2', 'haching_n', '1efc_pro_noise01']
                    prev_index = 0
                    for i in range(len(xfbin_mat.texture_groups[0].textures)):
                        if i == 0:
                            globals()[f'image_name_{i}'] = xfbin_mat.texture_groups[0].textures[i].texture
                            globals()[f'uv_{i}'] = material.node_tree.nodes.new('ShaderNodeUVMap')
                            globals()[f'uv_{i}'].uv_map = f'UV_{i}'
                            globals()[f'tex_{i}'] = material.node_tree.nodes.new('ShaderNodeTexImage')
                            globals()[f'tex_{i}'].name = f'Texture_{i}'
                            globals()[f'tex_{i}'].image = bpy.data.images.get(globals()[f'image_name_{i}'])
                            material.node_tree.links.new(globals()[f'uv_{i}'].outputs[0], globals()[f'tex_{i}'].inputs[0])
                            pBSDF = material.node_tree.nodes.get('Principled BSDF')
                            material.node_tree.links.new(globals()[f'tex_{i}'].outputs[0], pBSDF.inputs['Base Color'])
                            material.node_tree.links.new(globals()[f'tex_{i}'].outputs[1], pBSDF.inputs['Alpha'])
                            prev_index = i
                            print(prev_index)
                        if i > 0 and xfbin_mat.texture_groups[0].textures[i].texture_name not in not_included:
                            globals()[f'image_name_{i}'] = xfbin_mat.texture_groups[0].textures[i].texture
                            globals()[f'uv_{i}'] = material.node_tree.nodes.new('ShaderNodeUVMap')
                            globals()[f'uv_{i}'].uv_map = f'UV_{i}'
                            globals()[f'tex_{i}'] = material.node_tree.nodes.new('ShaderNodeTexImage')
                            globals()[f'tex_{i}'].name = f'Texture_{i}'
                            globals()[f'tex_{i}'].image = bpy.data.images.get(globals()[f'image_name_{i}'])
                            globals()[f'mix_{i}'] = material.node_tree.nodes.new('ShaderNodeMixRGB')
                            globals()[f'mix_{i}'].blend_type = 'MIX'
                            globals()[f'mix_{i}'].inputs[0].default_value = 1
                            material.node_tree.links.new(globals()[f'uv_{i}'].outputs[0], globals()[f'tex_{i}'].inputs[0])
                            material.node_tree.links.new(globals()[f'tex_{i}'].outputs[1], globals()[f'mix_{i}'].inputs[0])
                            material.node_tree.links.new(globals()[f'tex_{prev_index}'].outputs[0], globals()[f'mix_{i}'].inputs[1])
                            material.node_tree.links.new(globals()[f'tex_{i}'].outputs[0], globals()[f'mix_{i}'].inputs[2])
                            material.node_tree.links.new(globals()[f'mix_{i}'].outputs[0], pBSDF.inputs['Base Color'])
                            prev_index += 1
                            print(prev_index)
                o.material_slots[0].material = material
            
        return {'FINISHED'}

texture_chunks_property_groups = (
    XfbinTextureChunkPropertyGroup,
    TextureChunksListPropertyGroup,
)

texture_chunks_classes = (
    *texture_chunks_property_groups,
    XFBIN_PANEL_OT_OpenNut,
    XfbinTextureChunkPropertyPanel,
    RemakeShaders
)
