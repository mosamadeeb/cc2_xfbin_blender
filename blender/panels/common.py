from bpy.props import FloatProperty, IntProperty
from bpy.types import PropertyGroup, UILayout


def matrix_prop(ui_layout: UILayout, data, prop_name: str, length: int, text=''):
    ui_layout.label(text=text)
    box = ui_layout.box().grid_flow(row_major=True, columns=4, even_rows=True, even_columns=True)
    for i in range(length//4):
        for j in range(i*4, (i+1)*4):
            box.prop(data, prop_name, index=j, text='')


class IntPropertyGroup(PropertyGroup):
    value: IntProperty()


class FloatPropertyGroup(PropertyGroup):
    value: FloatProperty()


common_classes = [
    IntPropertyGroup,
    FloatPropertyGroup,
]
