from typing import List

import bpy
from bpy.props import (BoolProperty, CollectionProperty, IntProperty,
                       StringProperty)
from bpy.types import Action, Panel, PropertyGroup

from ...xfbin_lib.xfbin.structure.nucc import NuccChunkAnm
from ..common.helpers import XFBIN_TEXTURES_OBJ
from ..importer import make_actions
from .common import draw_xfbin_list


class XfbinAnmChunkPropertyGroup(PropertyGroup):
    def init_data(self, chunk: NuccChunkAnm, actions: List[Action]):
        pass


class AnmChunksListPropertyGroup(PropertyGroup):
    anm_chunks: CollectionProperty(
        type=XfbinAnmChunkPropertyGroup,
    )

    anm_chunk_index: IntProperty()

    def init_data(self, anm_chunks: List[NuccChunkAnm], context):
        self.anm_chunks.clear()
        for anm in anm_chunks:
            a: XfbinAnmChunkPropertyGroup = self.anm_chunks.add()
            a.init_data(anm, make_actions(anm, context))


anm_chunks_property_groups = (
    XfbinAnmChunkPropertyGroup,
    AnmChunksListPropertyGroup,
)

anm_chunks_classes = (
    *anm_chunks_property_groups,
)
