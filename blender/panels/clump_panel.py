from itertools import chain

import bpy
from bpy.props import (BoolProperty, CollectionProperty, FloatProperty,
                       FloatVectorProperty, IntProperty, StringProperty)
from bpy.types import Object, Panel, PropertyGroup

from ...xfbin_lib.xfbin.structure.nucc import (ClumpModelGroup,
                                               MaterialTextureGroup,
                                               NuccChunkClump,
                                               NuccChunkMaterial,
                                               NuccChunkTexture)
from ..common.helpers import format_hex_str, hex_str_to_int, int_to_hex_str
from .common import (EmptyPropertyGroup, draw_copy_paste_ops, draw_xfbin_list,
                     matrix_prop)


class XfbinNutTexturePropertyGroup(PropertyGroup):
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

    texture: StringProperty(
        name='Image Texture',
    )

    def update_name(self):
        self.name = self.texture_name

    def init_data(self, chunk: NuccChunkTexture):
        self.texture_name = chunk.name
        self.path = chunk.filePath
        self.texture = chunk.name


class XfbinTextureGroupPropertyGroup(PropertyGroup):
    def update_flag(self, context):
        self.update_name()

    flag: IntProperty(
        name='Flag',
        min=-0x80_00_00_00,
        max=0x7F_FF_FF_FF,
        update=update_flag,
    )

    textures: CollectionProperty(
        type=XfbinNutTexturePropertyGroup,
    )

    texture_index: IntProperty()

    def update_name(self):
        self.name = str(self.flag)

    def init_data(self, group: MaterialTextureGroup):
        self.flag = group.unk

        self.textures.clear()
        for chunk in group.texture_chunks:
            t: XfbinNutTexturePropertyGroup = self.textures.add()
            t.init_data(chunk)


class XfbinMaterialPropertyGroup(PropertyGroup):
    """Property group that contains attributes of a nuccChunkMaterial."""

    FLOATS_SIZE = 0x20

    def update_float_format(self, context):
        old_val = self.float_format
        new_val = format_hex_str(self.float_format, 1)

        if new_val and len(new_val) < 3:
            if old_val != new_val:
                self.float_format = new_val
        else:
            self.float_format = '00'

    def update_material_name(self, context):
        self.update_name()

    material_name: StringProperty(
        name='Material Name',
        default='new_material',
        update=update_material_name,
    )

    field02: IntProperty(
        name='Field02',
        min=0,
        max=255,
    )
    field04: FloatProperty(name='Field04')

    float_format: StringProperty(
        name='Float Format (Hex)',
        default='00',
        update=update_float_format,
    )
    floats: FloatVectorProperty(name='Floats', size=FLOATS_SIZE)

    texture_groups: CollectionProperty(
        type=XfbinTextureGroupPropertyGroup,
        name='Texture Groups',
    )

    texture_group_index: IntProperty()

    def update_name(self):
        self.name = self.material_name

    def init_data(self, material: NuccChunkMaterial):
        self.material_name = material.name

        self.field02 = material.field02
        self.field04 = material.field04

        self.float_format = int_to_hex_str(material.format, 1)
        self.floats = material.floats + ((0.0,) * (self.FLOATS_SIZE - len(material.floats)))

        self.texture_groups.clear()
        for group in material.texture_groups:
            g = self.texture_groups.add()
            g.init_data(group)


class ClumpModelGroupPropertyGroup(PropertyGroup):
    def update_unk(self, context):
        old_val = self.unk
        new_val = format_hex_str(self.unk, 4)

        if new_val and len(new_val) < 12:
            if old_val != new_val:
                self.unk = new_val
        else:
            self.unk = '00 00 00 00'

    flag0: IntProperty(
        name='Flag 1',
        min=0,
        max=255,
    )

    flag1: IntProperty(
        name='Flag 2',
        min=0,
        max=255,
    )

    unk: StringProperty(
        name='Unk',
        update=update_unk,
    )

    models: CollectionProperty(
        type=EmptyPropertyGroup,
    )

    model_index: IntProperty()

    def update_name(self):
        self.name = 'Group'

    def init_data(self, group: ClumpModelGroup):
        self.flag0 = group.flag0
        self.flag1 = group.flag1
        self.unk = int_to_hex_str(group.unk, 4)

        # Add models
        self.models.clear()
        for model in group.model_chunks:
            m: EmptyPropertyGroup = self.models.add()
            m.value = model.name if model else 'None'


class ClumpPropertyGroup(PropertyGroup):
    path: StringProperty(
        name='Chunk Path',
        description='XFBIN chunk path that will be used for identifying the clump in the XFBIN.\n'
        'Should be the same as the path of the clump in the XFBIN to inject to.\n'
        'Example: "c\\1nrt\max\\1nrtbod1.max"',
    )

    field00: IntProperty(
        name='Clump Unk',
    )

    coord_flag0: IntProperty(
        name='LOD Levels',
        min=0,
        max=255,
    )

    coord_flag1: IntProperty(
        name='LOD Flag 2',
        min=0,
        max=255,
    )

    model_flag0: IntProperty(
        name='Model Flag 1',
        min=0,
        max=255,
    )

    model_flag1: IntProperty(
        name='Model Flag 2',
        min=0,
        max=255,
    )

    models: CollectionProperty(
        type=EmptyPropertyGroup,
    )

    model_index: IntProperty()

    model_groups: CollectionProperty(
        type=ClumpModelGroupPropertyGroup,
    )

    model_group_index: IntProperty()

    materials: CollectionProperty(
        type=XfbinMaterialPropertyGroup,
        name='Xfbin Materials',
        description='Xfbin materials',
    )

    material_index: IntProperty()

    def init_data(self, clump: NuccChunkClump):
        self.path = clump.filePath

        # Set the properties
        self.field00 = clump.field00

        self.coord_flag0 = clump.coord_flag0
        self.coord_flag1 = clump.coord_flag1

        self.model_flag0 = clump.model_flag0
        self.model_flag1 = clump.model_flag1

        # Add models
        self.models.clear()
        for model in clump.model_chunks:
            m: EmptyPropertyGroup = self.models.add()
            m.value = model.name

        # Add model groups
        self.model_groups.clear()
        for group in clump.model_groups:
            g: ClumpModelGroupPropertyGroup = self.model_groups.add()
            g.init_data(group)
            g.name = 'Group'

        # Get all unique model chunks
        all_model_chunks = [i for i in dict.fromkeys(
            chain(clump.model_chunks, *map(lambda x: x.model_chunks, clump.model_groups))) if i is not None]

        # Get all unique material chunks
        material_chunks = list(dict.fromkeys(chain(*map(lambda x: x.material_chunks, all_model_chunks))))

        # Create a property group for each material
        self.materials.clear()
        for material in material_chunks:
            mat: XfbinMaterialPropertyGroup = self.materials.add()
            mat.init_data(material)

    def update_models(self, obj: Object):
        empties = [c for c in obj.children if c.type == 'EMPTY']

        for model in chain(self.models, *map(lambda x: x.models, self.model_groups)):
            empty = [e for e in empties if e.name == model.value]
            if empty:
                model.empty = empty[0]


class XfbinNutTexturePropertyPanel(Panel):
    bl_idname = 'OBJECT_PT_xfbin_texture'
    bl_parent_id = 'OBJECT_PT_xfbin_texture_group'
    bl_label = 'Textures'

    bl_space_type = 'PROPERTIES'
    bl_context = 'object'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        data: ClumpPropertyGroup = context.object.xfbin_clump_data
        mat: XfbinMaterialPropertyGroup = data.materials[data.material_index]
        return mat.texture_groups and mat.texture_group_index >= 0

    def draw(self, context):
        layout = self.layout
        obj = context.object
        data: ClumpPropertyGroup = obj.xfbin_clump_data
        mat: XfbinMaterialPropertyGroup = data.materials[data.material_index]
        group: XfbinTextureGroupPropertyGroup = mat.texture_groups[mat.texture_group_index]

        draw_xfbin_list(
            layout,
            5,
            group,
            f'xfbin_clump_data.materials[{data.material_index}].texture_groups[{mat.texture_group_index}]',
            'textures',
            'texture_index'
        )
        texture_index = group.texture_index

        if group.textures and texture_index >= 0:
            texture: XfbinNutTexturePropertyGroup = group.textures[texture_index]
            box = layout.box()

            box.prop(texture, 'texture_name')
            box.prop(texture, 'path')
            box.prop_search(texture, 'texture', bpy.data, 'images')


class XfbinTextureGroupPropertyPanel(Panel):
    bl_idname = 'OBJECT_PT_xfbin_texture_group'
    bl_parent_id = 'OBJECT_PT_xfbin_material'
    bl_label = 'Texture Groups'

    bl_space_type = 'PROPERTIES'
    bl_context = 'object'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        data: ClumpPropertyGroup = context.object.xfbin_clump_data
        return data.materials and data.material_index >= 0

    def draw(self, context):
        layout = self.layout
        obj = context.object
        data: ClumpPropertyGroup = obj.xfbin_clump_data
        mat: XfbinMaterialPropertyGroup = data.materials[data.material_index]

        draw_xfbin_list(
            layout, 4, mat, f'xfbin_clump_data.materials[{data.material_index}]', 'texture_groups', 'texture_group_index')
        texture_group_index = mat.texture_group_index

        if mat.texture_groups and texture_group_index >= 0:
            group: XfbinTextureGroupPropertyGroup = mat.texture_groups[texture_group_index]
            box = layout.box()

            box.prop(group, 'flag')


class XfbinMaterialPropertyPanel(Panel):
    """Panel that displays the XfbinMaterialPropertyGroup in the ClumpPropertyGroup of the selected armature object."""

    bl_idname = 'OBJECT_PT_xfbin_material'
    bl_parent_id = 'OBJECT_PT_xfbin_clump'
    bl_label = 'XFBIN Materials'

    bl_space_type = 'PROPERTIES'
    bl_context = 'object'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        data: ClumpPropertyGroup = obj.xfbin_clump_data

        draw_xfbin_list(layout, 3, data, f'xfbin_clump_data', 'materials', 'material_index')
        material_index = data.material_index

        if data.materials and material_index >= 0:
            material: XfbinMaterialPropertyGroup = data.materials[material_index]
            box = layout.box()

            box.prop(material, 'material_name')

            row = box.row()
            row.prop(material, 'field02')
            row.prop(material, 'field04')

            box.prop(material, 'float_format')
            matrix_prop(box, material, 'floats', NuccChunkMaterial.float_count(
                hex_str_to_int(material.float_format)), text='Floats')


class ClumpModelGroupPropertyPanel(Panel):
    bl_idname = 'OBJECT_PT_xfbin_model_group'
    bl_parent_id = 'OBJECT_PT_xfbin_clump'
    bl_label = 'Model Groups'

    bl_space_type = 'PROPERTIES'
    bl_context = 'object'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        data: ClumpPropertyGroup = obj.xfbin_clump_data

        draw_xfbin_list(layout, 1, data, f'xfbin_clump_data', 'model_groups', 'model_group_index')
        index = data.model_group_index

        if data.model_groups and index >= 0:
            group: ClumpModelGroupPropertyGroup = data.model_groups[index]
            box = layout.box()

            row = box.row()
            row.prop(group, 'flag0')
            row.prop(group, 'flag1')

            box.prop(group, 'unk')

            box.label(text='Models')
            draw_xfbin_list(box, 2, group, f'xfbin_clump_data.model_groups[{index}]', 'models', 'model_index')
            model_index = group.model_index

            if group.models and model_index >= 0:
                model: EmptyPropertyGroup = group.models[model_index]
                box = box.box()

                box.prop_search(model, 'empty', context.collection, 'all_objects',
                                text='Model Object', icon='OUTLINER_OB_EMPTY')


class ClumpPropertyPanel(Panel):
    """Panel that displays the ClumpPropertyPanel attached to the selected armature object."""

    bl_idname = 'OBJECT_PT_xfbin_clump'
    bl_label = '[XFBIN] Clump Properties'

    bl_space_type = 'PROPERTIES'
    bl_context = 'object'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'ARMATURE'

    def draw(self, context):
        obj = context.object
        layout = self.layout
        data: ClumpPropertyGroup = obj.xfbin_clump_data

        draw_copy_paste_ops(layout, 'xfbin_clump_data', 'Clump Properties')

        layout.label(text='LOD Flags:')
        box = layout.box()
        row = box.row()
        row.prop(data, 'coord_flag0')
        row.prop(data, 'coord_flag1')

        layout.prop(data, 'path')

        layout.label(text='Models')
        draw_xfbin_list(layout, 0, data, f'xfbin_clump_data', 'models', 'model_index')
        model_index = data.model_index


        if data.models and model_index >= 0:
            model: EmptyPropertyGroup = data.models[model_index]
            box = layout.box()

            box.prop_search(model, 'empty', context.collection, 'all_objects',
                            text='Model Object', icon='OUTLINER_OB_EMPTY')


clump_property_groups = (
    XfbinNutTexturePropertyGroup,
    XfbinTextureGroupPropertyGroup,
    XfbinMaterialPropertyGroup,
    ClumpModelGroupPropertyGroup,
    ClumpPropertyGroup,
)

clump_classes = (
    *clump_property_groups,
    ClumpPropertyPanel,
    ClumpModelGroupPropertyPanel,
    XfbinMaterialPropertyPanel,
    XfbinTextureGroupPropertyPanel,
    XfbinNutTexturePropertyPanel,
)
