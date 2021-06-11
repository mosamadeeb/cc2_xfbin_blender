from itertools import chain

import bpy
from bpy.props import (CollectionProperty, FloatProperty, FloatVectorProperty,
                       IntProperty, StringProperty)
from bpy.types import Operator, Panel, PropertyGroup

from ...xfbin_lib.xfbin.structure.nucc import (MaterialTextureGroup,
                                               NuccChunkClump,
                                               NuccChunkMaterial,
                                               NuccChunkTexture)
from ..common.helpers import format_hex_str, hex_str_to_int, int_to_hex_str
from .common import matrix_prop


def register_material_panel():
    """Creates a subclass of XfbinMaterialPropertyPanel with a new id and registers it."""

    panel_idname = f'OBJECT_PT_xfbin_material_{ClumpPropertyPanel.panel_count}'
    panel = type(panel_idname,
                 (XfbinMaterialPropertyPanel, Panel, ),
                 {'bl_idname': panel_idname,
                  'panel_id': f'{ClumpPropertyPanel.panel_count}'},
                 )

    ClumpPropertyPanel.panel_count += 1
    bpy.utils.register_class(panel)

    ClumpPropertyPanel.material_panels.append(panel)


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
        subtype='UNSIGNED',
        update=update_flag,
    )

    textures: CollectionProperty(
        type=XfbinNutTexturePropertyGroup,
    )

    def update_name(self):
        self.name = str(self.flag)

    def init_data(self, group: MaterialTextureGroup):
        self.flag = group.unk

        self.textures.clear()
        for chunk in group.texture_chunks:
            t = self.textures.add()
            t.init_data(chunk)
            t.name = chunk.name


class XfbinMaterialPropertyGroup(PropertyGroup):
    """Property group that contains attributes of a nuccChunkMaterial."""

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
    floats: FloatVectorProperty(name='Floats', size=16)

    texture_groups: CollectionProperty(
        type=XfbinTextureGroupPropertyGroup,
        name='Texture Groups',
    )

    def update_name(self):
        self.name = self.material_name

    def init_data(self, material: NuccChunkMaterial):
        self.material_name = material.name

        self.field02 = material.field02
        self.field04 = material.field04

        self.float_format = int_to_hex_str(material.format, 1)
        self.floats = material.floats + ((0.0,) * (16 - len(material.floats)))

        self.texture_groups.clear()
        for group in material.texture_groups:
            g = self.texture_groups.add()
            g.init_data(group)

        # self.texture_group_flags = list(map(lambda x: x.unk, material.texture_groups)) + \
        #     ([0] * (8 - len(material.texture_groups)))


class AddXfbinMaterialOperator(Operator):
    bl_idname = 'xfbin.add_xfbin_material'
    bl_label = 'Add New Material'

    def execute(self, context):
        materials = context.object.xfbin_clump_data.materials
        active_panel_ids = context.object.xfbin_clump_data.active_panel_ids

        new_mat = materials.add()
        new_mat.name = new_mat.material_name
        new_id = active_panel_ids.add()

        if ClumpPropertyPanel.panel_count < len(materials):
            register_material_panel()

        new_id.name = f'{ClumpPropertyPanel.material_panels[len(materials) - 1].panel_id}'

        return {'FINISHED'}


class DeleteXfbinMaterialOperator(Operator):
    bl_idname = 'xfbin.delete_xfbin_material'
    bl_label = 'Remove'

    panel_id: StringProperty(description='Contains the id of the panel that contains this operator')

    def execute(self, context):
        materials = context.object.xfbin_clump_data.materials
        active_panel_ids = context.object.xfbin_clump_data.active_panel_ids

        mat_index = active_panel_ids.find(self.panel_id)

        active_panel_ids.remove(mat_index)
        materials.remove(mat_index)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class XfbinMaterialPropertyPanel(Panel):
    """Panel that displays the XfbinMaterialPropertyGroup in the ClumpPropertyGroup of the selected armature object."""

    bl_idname = 'OBJECT_PT_xfbin_material'
    bl_parent_id = 'OBJECT_PT_xfbin_clump'
    bl_label = ''

    bl_space_type = 'PROPERTIES'
    bl_context = 'object'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}

    panel_id: str

    @classmethod
    def poll(cls, context):
        return context.object.xfbin_clump_data.active_panel_ids.find(cls.panel_id) != -1

    def draw_header(self, context):
        layout = self.layout
        mat_index = context.object.xfbin_clump_data.active_panel_ids.find(self.panel_id)

        if mat_index == -1:
            return

        material = context.object.xfbin_clump_data.materials[mat_index]

        layout.label(text=f'Material {mat_index + 1}:  {material.material_name}')

    def draw(self, context):
        layout = self.layout
        mat_index = context.object.xfbin_clump_data.active_panel_ids.find(self.panel_id)

        if mat_index == -1:
            return

        # Get the material to be shown in this panel
        material = context.object.xfbin_clump_data.materials[mat_index]

        op = layout.operator(operator='xfbin.delete_xfbin_material', icon='X')
        op.panel_id = self.panel_id

        layout.prop(material, 'material_name')

        row = layout.row()
        row.prop(material, 'field02')
        row.prop(material, 'field04')

        layout.prop(material, 'float_format')
        matrix_prop(layout, material, 'floats', NuccChunkMaterial.float_count(
            hex_str_to_int(material.float_format)), text='Floats')

        #matrix_prop(layout, material, 'texture_group_flags', 8, text='Texture Group Flags')


class ClumpPropertyGroup(PropertyGroup):
    path: StringProperty(
        name='Chunk Path',
        description='XFBIN chunk path that will be used for identifying the clump in the XFBIN.\n'
        'Should be the same as the path of the clump in the XFBIN to inject to.\n'
        'Example: "c\\1nrt\max\\1nrtbod1.max"',
    )

    materials: CollectionProperty(
        type=XfbinMaterialPropertyGroup,
        name='Xfbin Materials',
        description='Xfbin materials',
    )

    active_panel_ids: CollectionProperty(
        type=PropertyGroup,
        description='Each element is a panel id and its index is the index of the material in the materials collection',
    )

    def init_data(self, clump: NuccChunkClump):
        self.path = clump.filePath

        # Get all unique material chunks
        material_chunks = list(dict.fromkeys(chain(*map(lambda x: x.material_chunks, clump.model_chunks))))

        self.active_panel_ids.clear()

        # Register new material panels as required
        for _ in range(len(material_chunks) - ClumpPropertyPanel.panel_count):
            register_material_panel()

        # Create a property group for each material
        for i, material in enumerate(material_chunks):
            mat: XfbinMaterialPropertyGroup = self.materials.add()
            mat.init_data(material)
            mat.name = mat.material_name

            new_id = self.active_panel_ids.add()
            new_id.name = f'{ClumpPropertyPanel.material_panels[i].panel_id}'


class ClumpPropertyPanel(Panel):
    """Panel that displays the ClumpPropertyPanel attached to the selected armature object."""

    bl_idname = 'OBJECT_PT_xfbin_clump'
    bl_label = '[XFBIN] Clump Properties'

    bl_space_type = 'PROPERTIES'
    bl_context = 'object'
    bl_region_type = 'WINDOW'

    panel_count = 0
    material_panels = list()

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'ARMATURE'

    def draw(self, context):
        obj = context.object
        layout = self.layout

        layout.prop(obj.xfbin_clump_data, 'path')
        layout.label(text='XFBIN Materials:')
        layout.operator(operator='xfbin.add_xfbin_material', icon='ADD')


clump_classes = [
    AddXfbinMaterialOperator,
    DeleteXfbinMaterialOperator,
    XfbinNutTexturePropertyGroup,
    XfbinTextureGroupPropertyGroup,
    XfbinMaterialPropertyGroup,
    ClumpPropertyGroup,
    ClumpPropertyPanel,
]
