import bpy
from bpy.props import (CollectionProperty, EnumProperty, IntProperty,
                       StringProperty)
from bpy.types import Panel, PropertyGroup

from ...xfbin_lib.xfbin.structure.nud import (NudMaterial, NudMaterialProperty,
                                              NudMaterialTexture, NudMesh)
from ..common.helpers import format_hex_str, int_to_hex_str
from .common import FloatPropertyGroup, draw_xfbin_list


class NudMaterialPropPropertyGroup(PropertyGroup):
    def update_prop_name(self, context):
        self.update_name()

    prop_name: StringProperty(
        name='Property name',
        default='NU_useStColor',  # This usually has no values, so it's safe to have it as the default name
        update=update_prop_name,
    )

    count: IntProperty(
        name='Value count',
        min=0,
        max=0xFF,
    )

    values: CollectionProperty(
        type=FloatPropertyGroup,
        name='Values',
    )

    def update_name(self):
        self.name = self.prop_name

    def init_data(self, material_prop: NudMaterialProperty):
        self.prop_name = material_prop.name
        self.count = len(material_prop.values)

        self.values.clear()
        for val in material_prop.values:
            f = self.values.add()
            f.value = val


class NudMaterialTexturePropertyGroup(PropertyGroup):
    def update_unk0(self, context):
        self.update_name()

    unk0: IntProperty(
        name='Unk 0',
        min=-0x80_00_00_00,
        max=0x7F_FF_FF_FF,
        update=update_unk0,
    )

    map_mode: IntProperty(
        name='Map mode',
        min=0,
        max=0xFF_FF,
    )

    wrap_mode_s: IntProperty(
        name='Wrap mode S',
        min=0,
        max=0xFF,
    )

    wrap_mode_t: IntProperty(
        name='Wrap mode T',
        min=0,
        max=0xFF,
    )

    min_filter: IntProperty(
        name='Min filter',
        min=0,
        max=0xFF,
    )

    mag_filter: IntProperty(
        name='Mag filter',
        min=0,
        max=0xFF
    )

    mip_detail: IntProperty(
        name='Mip detail',
        min=0,
        max=0xFF,
    )

    unk1: IntProperty(
        name='Unk 1',
        min=0,
        max=0xFF,
    )

    unk2: IntProperty(
        name='Unk 2',
        min=-0x80_00,
        max=0x7F_FF,
    )

    def update_name(self):
        self.name = str(self.unk0)

    def init_data(self, texture: NudMaterialTexture):
        self.unk0 = texture.unk0
        self.map_mode = texture.mapMode
        self.wrap_mode_s = texture.wrapModeS
        self.wrap_mode_t = texture.wrapModeT
        self.min_filter = texture.minFilter
        self.mag_filter = texture.magFilter
        self.mip_detail = texture.mipDetail
        self.unk1 = texture.unk1
        self.unk2 = texture.unk2


class NudMaterialPropertyGroup(PropertyGroup):
    def update_material_id(self, context):
        old_val = self.material_id
        new_val = format_hex_str(self.material_id, 4)

        if new_val and len(new_val) < 12:
            if old_val != new_val:
                self.material_id = new_val
        else:
            self.material_id = '00 00 00 00'

        self.update_name()

    material_id: StringProperty(
        name='Material ID (Hex)',
        default='00 00 F0 0A',  # Just a generic material ID from Storm 4
        update=update_material_id,
    )

    source_factor: IntProperty(
        name='Source Factor',
        min=0,
        max=0xFF_FF,
    )

    dest_factor: IntProperty(
        name='Destination Factor',
        min=0,
        max=0xFF_FF,
    )

    alpha_test: IntProperty(
        name='Alpha Test',
        min=0,
        max=0xFF,
    )

    alpha_function: IntProperty(
        name='Alpha Function',
        min=0,
        max=0xFF,
    )

    ref_alpha: IntProperty(
        name='Reference Alpha',
        min=0,
        max=0xFF_FF,
    )

    cull_mode: IntProperty(
        name='Cull Mode',
        min=0,
        max=0xFF_FF,
        default=0x405,
    )

    zbuffer_offset: IntProperty(
        name='ZBuffer Offset',
        min=-0x80_00_00_00,
        max=0x7F_FF_FF_FF,
    )

    textures: CollectionProperty(
        type=NudMaterialTexturePropertyGroup
    )

    material_props: CollectionProperty(
        type=NudMaterialPropPropertyGroup
    )

    def update_name(self):
        self.name = self.material_id

    def init_data(self, material: NudMaterial):
        self.material_id = int_to_hex_str(material.flags, 4)

        self.source_factor = material.sourceFactor
        self.dest_factor = material.destFactor
        self.alpha_test = material.alphaTest
        self.alpha_function = material.alphaFunction
        self.ref_alpha = material.refAlpha
        self.cull_mode = material.cullMode
        self.zbuffer_offset = material.zBufferOffset

        # Add textures
        self.textures.clear()
        for texture in material.textures:
            t = self.textures.add()
            t.init_data(texture)

        # Add material props
        self.material_props.clear()
        for property in material.properties:
            p = self.material_props.add()
            p.init_data(property)


class NudMeshPropertyGroup(PropertyGroup):
    """Property group that contains attributes of a nuccChunkModel."""

    vertex_type: EnumProperty(
        name='Vertex Format',
        items=[
            ('0', 'No normals', ''),
            ('1', 'Normals (Float)', ''),
            ('2', 'Unknown', ''),
            ('3', 'Normals/Tan/Bitan (Float)', ''),
            ('6', 'Normals (Half float)', ''),
            ('7', 'Normals/Tan/Bitan (Half float)', ''),
        ],
        default='3',
        description='Format to save the vertices in when writing.\n'
        'Note: Do NOT change this unless you know what you are doing',
    )

    bone_type: EnumProperty(
        name='Bone Format',
        items=[
            ('0', 'No bones', ''),
            ('16', 'Bones (Float)', ''),
            ('32', 'Bones (Half float)', ''),
            ('64', 'Bones (Byte)', ''),
        ],
        default='16',
        description='Format to save the bones in when writing.\n'
        'Note: Do NOT change this unless you know what you are doing',
    )

    uv_type: EnumProperty(
        name='Vertex Color Format',
        items=[
            ('0', 'No color', ''),
            ('2', 'Color (Byte)', ''),
            ('4', 'Color (Half float)', ''),
        ],
        default='2',
        description='Format to save the vertex color in when writing.\n'
        'Note: Do NOT change this unless you know what you are doing',
    )

    xfbin_material: StringProperty(
        name='XFBIN Material',
        description='The XFBIN material that this mesh uses'
    )

    materials: CollectionProperty(
        type=NudMaterialPropertyGroup,
        name='Materials',
        description='Materials used by this NUD mesh'
    )

    material_index: IntProperty()

    def init_data(self, mesh: NudMesh, xfbin_mat_name: str):
        self.vertex_type = str(int(mesh.vertex_type))
        self.bone_type = str(int(mesh.bone_type))
        self.uv_type = str(int(mesh.uv_type))

        self.xfbin_material = xfbin_mat_name

        self.materials.clear()
        for material in mesh.materials:
            m = self.materials.add()
            m.init_data(material)

        self.material_index = 0


class NudMeshPropertyPanel(Panel):
    """Panel that displays the NudMeshPropertyGroup attached to the selected mesh object."""

    bl_idname = 'OBJECT_PT_nud_mesh'
    bl_label = "[XFBIN] Mesh Properties"

    bl_space_type = "PROPERTIES"
    bl_context = "object"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' \
            and obj.parent and obj.parent.type == 'EMPTY' \
            and obj.parent.parent and obj.parent.parent.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        data: NudMeshPropertyGroup = obj.xfbin_mesh_data

        layout.prop(data, 'vertex_type')
        layout.prop(data, 'bone_type')
        layout.prop(data, 'uv_type')

        layout.prop_search(data, 'xfbin_material', obj.parent.parent.xfbin_clump_data, 'materials')

        index = draw_xfbin_list(layout, data, 'xfbin_mesh_data', 'materials', 'material_index')

        if index is not None:
            layout.prop(data.materials[index], 'material_id')


nud_mesh_classes = [
    NudMaterialPropPropertyGroup,
    NudMaterialTexturePropertyGroup,
    NudMaterialPropertyGroup,
    NudMeshPropertyGroup,
    NudMeshPropertyPanel,
]
