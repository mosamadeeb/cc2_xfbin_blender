import bpy
from bpy.props import FloatProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import Operator, PropertyGroup, UILayout, UIList


def matrix_prop(ui_layout: UILayout, data, prop_name: str, length: int, text=''):
    ui_layout.label(text=text)
    box = ui_layout.box().grid_flow(row_major=True, columns=4, even_rows=True, even_columns=True)
    for i in range(length//4):
        for j in range(i*4, (i+1)*4):
            box.prop(data, prop_name, index=j, text='')

    for i in range((length // 4) * 4, (length // 4) * 4 + (length % 4)):
        box.prop(data, prop_name, index=i, text='')


def matrix_prop_group(ui_layout: UILayout, data, prop_name: str, length: int, text=''):
    collection = data.path_resolve(prop_name)
    ui_layout.label(text=text)
    box = ui_layout.box().grid_flow(row_major=True, columns=4, even_rows=True, even_columns=True)
    for i in range(length//4):
        for j in range(i*4, (i+1)*4):
            box.prop(collection[j], 'value', text='')

    for i in range((length // 4) * 4, (length // 4) * 4 + (length % 4)):
        box.prop(collection[i], 'value', text='')


class IntPropertyGroup(PropertyGroup):
    value: IntProperty()


class FloatPropertyGroup(PropertyGroup):
    value: FloatProperty()


class EmptyPropertyGroup(PropertyGroup):
    def update_empty(self, context):
        if self.empty:
            self.value = self.empty.name
        
    def update_value(self, context):
        self.update_name()

    def poll_empty(self, object):
        return object.type == 'EMPTY' and object.parent and object.parent.type == 'ARMATURE'

    empty: PointerProperty(
        type=bpy.types.Object,
        update=update_empty,
        poll=poll_empty,
    )

    value: StringProperty(
        update=update_value,
    )

    def update_name(self):
        self.name = self.value


# UIList code adapted from here https://sinestesia.co/blog/tutorials/using-uilists-in-blender/
class XFBIN_LIST_UL_List(UIList):
    """UIList."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')


class XFBIN_LIST_OT_NewItem(Operator):
    """Add a new item to the list."""

    bl_idname = 'xfbin_list.new_item'
    bl_label = 'Add a new item'

    prop_path: StringProperty()
    collection: StringProperty()
    index: StringProperty()

    def execute(self, context):
        prop = context.object.path_resolve(self.prop_path)
        collection = prop.path_resolve(self.collection)

        collection.add().update_name()
        return{'FINISHED'}


class XFBIN_LIST_OT_DeleteItem(Operator):
    """Delete the selected item from the list."""

    bl_idname = 'xfbin_list.delete_item'
    bl_label = 'Deletes an item'

    prop_path: StringProperty()
    collection: StringProperty()
    index: StringProperty()

    def execute(self, context):
        prop = context.object.path_resolve(self.prop_path)
        collection = prop.path_resolve(self.collection)
        index = prop.path_resolve(self.index)

        if collection:
            collection.remove(index)
            prop[self.index] = min(max(0, index - 1), len(collection) - 1)

        return{'FINISHED'}


class XFBIN_LIST_OT_MoveItem(Operator):
    """Move an item in the list."""

    bl_idname = 'xfbin_list.move_item'
    bl_label = 'Move an item in the list'

    direction: bpy.props.EnumProperty(
        items=(
            ('UP', 'Up', ''),
            ('DOWN', 'Down', ''),
        )
    )

    prop_path: StringProperty()
    collection: StringProperty()
    index: StringProperty()

    def execute(self, context):
        prop = context.object.path_resolve(self.prop_path)
        collection = prop.path_resolve(self.collection)
        index = prop.path_resolve(self.index)

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        collection.move(neighbor, index)

        # Move index of an item render queue while clamping it.
        list_length = len(collection) - 1
        new_index = index + (-1 if self.direction == 'UP' else 1)

        prop[self.index] = max(0, min(new_index, list_length))

        return{'FINISHED'}


def draw_xfbin_list(layout: UILayout, data, path: str, collection_name: str, index_name: str):
    """Draws a list using the layout and populates it with the given collection and index."""

    row = layout.row()
    row.template_list('XFBIN_LIST_UL_List', 'xfbin_list', data, collection_name, data, index_name)

    row = layout.row()
    for op, txt, icn in (('new_item', 'New', 'ADD'), ('delete_item', 'Remove', 'REMOVE'), ('move_item', 'Up', 'TRIA_UP'), ('move_item', 'Down', 'TRIA_DOWN')):
        opr = row.operator(f'xfbin_list.{op}', text=txt, icon=icn)
        opr.prop_path = path
        opr.collection = collection_name
        opr.index = index_name

        if op == 'move_item':
            opr.direction = txt.upper()

    layout.label(text='Selected Item:')


common_classes = [
    IntPropertyGroup,
    FloatPropertyGroup,
    EmptyPropertyGroup,
    XFBIN_LIST_UL_List,
    XFBIN_LIST_OT_NewItem,
    XFBIN_LIST_OT_DeleteItem,
    XFBIN_LIST_OT_MoveItem,
]
