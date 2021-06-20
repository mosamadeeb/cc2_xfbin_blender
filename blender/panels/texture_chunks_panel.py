from typing import List

import bpy
from bpy.props import (BoolProperty, CollectionProperty, IntProperty,
                       StringProperty)
from bpy.types import Panel, PropertyGroup

from ...xfbin_lib.xfbin.structure.nucc import NuccChunkTexture
from .common import draw_xfbin_list


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
        self.texture = chunk.name

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
    bl_label = 'Texture Chunks'

    bl_space_type = 'PROPERTIES'
    bl_context = 'object'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'EMPTY' and context.object.parent is None

    def draw(self, context):
        layout = self.layout
        obj = context.object
        data: TextureChunksListPropertyGroup = obj.xfbin_texture_chunks_data

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


texture_chunks_property_groups = (
    XfbinTextureChunkPropertyGroup,
    TextureChunksListPropertyGroup,
)

texture_chunks_classes = (
    *texture_chunks_property_groups,
    XFBIN_PANEL_OT_OpenNut,
    XfbinTextureChunkPropertyPanel,
)
