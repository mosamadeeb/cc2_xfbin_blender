import importlib.util

blender_loader = importlib.util.find_spec('bpy')

bl_info = {
    "name": "CyberConnect2 XFBIN File Import/Export",
    "author": "SutandoTsukai181",
    "version": (1, 0, 1),
    "blender": (2, 90, 0),
    "location": "File > Import-Export",
    "description": "Import/Export XFBIN model files found in CyberConnect2 Naruto Storm and JoJo games.",
    "warning": "",
    "doc_url": "https://github.com/SutandoTsukai181/cc2_xfbin_blender/wiki",
    "wiki_url": "https://github.com/SutandoTsukai181/cc2_xfbin_blender/wiki",
    "tracker_url": "https://github.com/SutandoTsukai181/cc2_xfbin_blender/issues",
    "category": "Import-Export",
}

if blender_loader:
    from .blender.addon import *
