import bpy
from bpy.props import (EnumProperty, FloatVectorProperty, IntProperty,
                       IntVectorProperty, StringProperty)
from bpy.types import Panel, PropertyGroup

from ...xfbin_lib.xfbin.structure.nucc import NuccChunkModel, RiggingFlag
from ..common.coordinate_converter import pos_cm_to_m_tuple
from .common import draw_copy_paste_ops, matrix_prop


class NudPropertyGroup(PropertyGroup):
    """Property group that contains attributes of a nuccChunkModel."""

    mesh_bone: StringProperty(
        name='Mesh Bone',
        description='The bone that this NUD is attached to'
    )

    rigging_flag: EnumProperty(
        name='Rigging Flag',
        items=[('1', 'Unskinned (0x01)', ''),
               ('2', 'Skinned (0x02)', ''),
               ('4', 'Outline (0x04)', ''), ],
        description='Affects the NUD\'s rigging. Unskinned and Skinned should not be enabled at the same time. Examples:\n'
        'Eyes (Storm): Unskinned (0x01)\n'
        'Eyes (JoJo): Skinned (0x02)\n'
        'Teeth (Storm): Unskinned & Body (0x05)\n'
        'Teeth (JoJo): Unskinned (0x01)\n'
        'Body and tongue: Skinned & Body (0x06)\n',
        options={'ENUM_FLAG'},
        default={'2', '4'},
    )

    rigging_flag_extra: EnumProperty(
        name='Rigging Flag (Extra)',
        items=[('16', 'Blur (0x10)', ''),
               ('32', 'Shadow (0x20)', ''), ],
        description='Both are usually always on',
        options={'ENUM_FLAG'},
        default={'16', '32'},
    )

    bone_flag: IntProperty(
        name='Bone Flag',
        min=0,
        max=255,
        default=0x14,
    )

    material_flags: IntVectorProperty(
        name='Material Flags',
        description='Affects shading and transparency',
        size=4,
        min=0,
        max=255,
        default=(0, 0, 8, 3),
    )

    flag1_floats: FloatVectorProperty(
        name='Material Floats',
        description='Only applies when the second flag (index 1) in the material flags contains 0x04',
        size=6,
    )

    bounding_sphere_nud: FloatVectorProperty(
        name='Bounding Sphere (NUD)',
        size=4,
    )

    bounding_sphere_group: FloatVectorProperty(
        name='Bounding Sphere (Group)',
        size=8,
    )

    def init_data(self, model: NuccChunkModel, mesh_bone: str):
        self.mesh_bone = mesh_bone

        # Set the rigging flag
        rigging_flag = set()
        if model.rigging_flag & RiggingFlag.UNSKINNED:
            rigging_flag.add('1')
        if model.rigging_flag & RiggingFlag.SKINNED:
            rigging_flag.add('2')
        if model.rigging_flag & RiggingFlag.OUTLINE:
            rigging_flag.add('4')

        self.rigging_flag = rigging_flag

        # Set the extra rigging flag
        rigging_flag_extra = set()
        if model.rigging_flag & RiggingFlag.BLUR:
            rigging_flag_extra.add('16')
        if model.rigging_flag & RiggingFlag.SHADOW:
            rigging_flag_extra.add('32')

        self.rigging_flag_extra = rigging_flag_extra

        # Get the first (and only) group's bounding sphere and bone flag
        groups = model.nud.mesh_groups
        if groups:
            self.bone_flag = groups[0].bone_flags
            self.bounding_sphere_group = pos_cm_to_m_tuple(tuple(groups[0].bounding_sphere))

        # Set the material flags
        self.material_flags = tuple(model.material_flags)

        # Set the flag1 floats
        self.flag1_floats = model.flag1_floats if model.flag1_floats else [0] * 6

        # Set the NUD's bounding sphere
        self.bounding_sphere_nud = pos_cm_to_m_tuple(tuple(model.nud.bounding_sphere))


class NudPropertyPanel(Panel):
    """Panel that displays the NudPropertyGroup attached to the selected empty object."""

    bl_idname = 'OBJECT_PT_nud'
    bl_label = "[XFBIN] NUD Properties"

    bl_space_type = "PROPERTIES"
    bl_context = "object"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'EMPTY' and obj.parent and obj.parent.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        data: NudPropertyGroup = obj.xfbin_nud_data

        draw_copy_paste_ops(layout, 'xfbin_nud_data', 'NUD Properties')

        layout.prop_search(data, 'mesh_bone', obj.parent.data, 'bones')

        layout.label(text='Rigging Flags')
        box = layout.box()
        box.prop(data, 'rigging_flag')
        box.prop(data, 'rigging_flag_extra')

        layout.prop(data, 'bone_flag')

        layout.prop(data, 'material_flags')

        if data.material_flags[1] & 0x04:
            layout.prop(data, 'flag1_floats')

        matrix_prop(layout, data, 'bounding_sphere_nud', 4, 'Bounding Sphere (NUD)')
        matrix_prop(layout, data, 'bounding_sphere_group', 8, 'Bounding Sphere (Group)')


nud_property_groups = (
    NudPropertyGroup,
)

nud_classes = (
    *nud_property_groups,
    NudPropertyPanel,
)
