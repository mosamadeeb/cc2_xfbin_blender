import bpy
from bpy.props import PointerProperty

from .importer import ImportXFBIN, menu_func_import
from .panels.nud_panel import NudPropertyGroup, NudPropertyPanel

classes = (
    ImportXFBIN,
    NudPropertyGroup,
    NudPropertyPanel,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    # add to the export / import menu
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    # Add Xfbin and Nud properties data
    bpy.types.Object.xfbin_nud_data = PointerProperty(type=NudPropertyGroup)  # Applies to empties only


def unregister():
    del bpy.types.Object.xfbin_nud_data
    for c in classes:
        bpy.utils.unregister_class(c)

    # remove from the export / import menu
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
