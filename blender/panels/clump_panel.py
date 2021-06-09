from itertools import chain

import bpy
from bpy.props import (CollectionProperty, FloatProperty, FloatVectorProperty,
                       IntProperty, IntVectorProperty, StringProperty)
from bpy.types import Operator, Panel, PropertyGroup

from ...xfbin_lib.xfbin.structure.nucc import NuccChunkClump, NuccChunkMaterial
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


class XfbinMaterialPropertyGroup(PropertyGroup):
    """Property group that contains attributes of a nuccChunkMaterial."""

    material_name: StringProperty(name='Material Name',
                                  default='new_material',
                                  )

    field02: IntProperty(name='Field02')
    field04: FloatProperty(name='Field04')

    float_format: StringProperty(name='Float Format (Hex)',
                                 default='00',
                                 )
    floats: FloatVectorProperty(name='Floats', size=16)

    texture_group_flags: IntVectorProperty(name='Texture Group Flags', size=8)

    def init_data(self, material: NuccChunkMaterial):
        self.material_name = material.name

        self.field02 = material.field02
        self.field04 = material.field04

        self.float_format = f'{material.format:02X}'
        self.floats = material.floats + ((0.0,) * (16 - len(material.floats)))

        self.texture_group_flags = list(map(lambda x: x.unk, material.texture_groups)) + \
            ([0] * (8 - len(material.texture_groups)))


class AddXfbinMaterialOperator(Operator):
    bl_idname = 'xfbin.add_xfbin_material'
    bl_label = 'Add New Material'

    def execute(self, context):
        materials = context.object.xfbin_clump_data.materials
        active_panel_ids = context.object.xfbin_clump_data.active_panel_ids

        materials.add()
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
        matrix_prop(layout, material, 'floats', 16, text='Floats')

        matrix_prop(layout, material, 'texture_group_flags', 8, text='Texture Group Flags')


class ClumpPropertyGroup(PropertyGroup):
    path: StringProperty(name='Chunk Path',
                         description='XFBIN chunk path that will be used for identifying the clump in the XFBIN.\n'
                         'Should be the same as the path of the clump in the XFBIN to inject to.\n'
                         'Example: "c\\1nrt\max\\1nrtbod1.max"',
                         )

    materials: CollectionProperty(type=XfbinMaterialPropertyGroup,
                                  name='Xfbin Materials',
                                  description='Xfbin materials',
                                  )

    active_panel_ids: CollectionProperty(type=PropertyGroup,
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
