import bpy
from bpy.props import PointerProperty

from .exporter import ExportXfbin, menu_func_export
from .importer import ImportXFBIN, menu_func_import
from .panels.clump_panel import (AddXfbinMaterialOperator, ClumpPropertyGroup,
                                 ClumpPropertyPanel,
                                 DeleteXfbinMaterialOperator,
                                 XfbinMaterialPropertyGroup)
from .panels.nud_panel import NudPropertyGroup, NudPropertyPanel

classes = (
    ImportXFBIN,
    ExportXfbin,
    AddXfbinMaterialOperator,
    DeleteXfbinMaterialOperator,
    XfbinMaterialPropertyGroup,
    ClumpPropertyGroup,
    ClumpPropertyPanel,
    NudPropertyGroup,
    NudPropertyPanel,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    # add to the export / import menu
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    # Add Xfbin and Nud properties data
    bpy.types.Object.xfbin_clump_data = PointerProperty(type=ClumpPropertyGroup)  # Applies to armatures only
    bpy.types.Object.xfbin_nud_data = PointerProperty(type=NudPropertyGroup)  # Applies to empties only


def unregister():
    del bpy.types.Object.xfbin_clump_data
    del bpy.types.Object.xfbin_nud_data

    for p in reversed(ClumpPropertyPanel.material_panels):
        bpy.utils.unregister_class(p)

    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    # remove from the export / import menu
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
