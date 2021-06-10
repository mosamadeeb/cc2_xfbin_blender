import bpy
from bpy.props import EnumProperty, FloatVectorProperty, IntVectorProperty, PointerProperty, StringProperty
from bpy.types import Bone, PropertyGroup

from ...xfbin_lib.xfbin.structure.nucc import NuccChunkModel, RiggingFlag


class NudPropertyGroup(PropertyGroup):
    """Property group that contains attributes of a nuccChunkModel."""

    mesh_bone: StringProperty(name='Mesh bone')

    rigging_flag: EnumProperty(name='Rigging flag',
                               items=[('1', 'Unskinned (0x01)', ''),
                                      ('2', 'Skinned (0x02)', ''),
                                      ('4', 'Body (0x04)', ''), ],
                               description='Affects the NUD\'s rigging. Unskinned and Skinned should not be enabled at the same time. Examples:\n'
                               'Eyes (Storm): Unskinned (0x01)\n'
                               'Eyes (JoJo): Skinned (0x02)\n'
                               'Teeth (Storm): Unskinned & Body (0x05)\n'
                               'Teeth (JoJo): Unskinned (0x01)\n'
                               'Body and tongue: Skinned & Body (0x06)\n',
                               options={'ENUM_FLAG'},
                               default={'2', '4'},
                               )

    rigging_flag_extra: EnumProperty(name='Rigging flag (extra)',
                                     items=[('16', 'Blur (0x10)', ''),
                                            ('32', 'Shadow (0x20)', ''), ],
                                     description='Both are usually always on',
                                     options={'ENUM_FLAG'},
                                     default={'16', '32'},
                                     )

    material_flags: IntVectorProperty(name='Material flags',
                                      description='Affects shading and transparency',
                                      size=4,
                                      min=0,
                                      max=255,
                                      default=(0, 0, 8, 3),
                                      )

    flag1_floats: FloatVectorProperty(name='Extra material floats',
                                      description='Only applies when the second flag (index 1) in the material flags contains 0x04',
                                      size=6,
                                      )

    def init_data(self, model: NuccChunkModel):

        # TODO: Change this to pointer property instead of string property
        self.mesh_bone = model.coord_chunk.name if model.coord_chunk else 'None'

        # Set the rigging flag
        rigging_flag = set()
        if model.rigging_flag & RiggingFlag.UNSKINNED:
            rigging_flag.add('1')
        if model.rigging_flag & RiggingFlag.SKINNED:
            rigging_flag.add('2')
        if model.rigging_flag & RiggingFlag.BODY:
            rigging_flag.add('4')

        self.rigging_flag = rigging_flag

        # Set the extra rigging flag
        rigging_flag_extra = set()
        if model.rigging_flag & RiggingFlag.BLUR:
            rigging_flag_extra.add('16')
        if model.rigging_flag & RiggingFlag.SHADOW:
            rigging_flag_extra.add('32')

        self.rigging_flag_extra = rigging_flag_extra

        # Set the material flags
        self.material_flags = tuple(model.material_flags)

        # Set the flag1 floats
        self.flag1_floats = model.flag1_floats if model.flag1_floats else [0] * 6


class NudPropertyPanel(bpy.types.Panel):
    """Panel that displays the NudPropertyGroup attached to the selected empty object."""

    bl_idname = 'OBJECT_PT_nud'
    bl_label = "[XFBIN] NUD Properties"

    bl_space_type = "PROPERTIES"
    bl_context = "object"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'EMPTY'

    def draw(self, context):
        layout = self.layout
        obj = context.object

        layout.prop(obj.xfbin_nud_data, 'mesh_bone')

        layout.label(text='Rigging flags')
        layout.prop(obj.xfbin_nud_data, 'rigging_flag')
        layout.prop(obj.xfbin_nud_data, 'rigging_flag_extra')

        layout.prop(obj.xfbin_nud_data, 'material_flags')

        layout.prop(obj.xfbin_nud_data, 'flag1_floats')
