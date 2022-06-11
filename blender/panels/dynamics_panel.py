from typing import List

import bpy
from bpy.props import (BoolProperty, CollectionProperty, IntProperty,
                       StringProperty, FloatProperty, EnumProperty)
from bpy.types import Panel, PropertyGroup

from ...xfbin_lib.xfbin.structure.nucc import NuccChunkDynamics, Dynamics1, Dynamics2
from ..common.helpers import XFBIN_DYNAMICS_OBJ
from .common import (EmptyPropertyGroup, draw_copy_paste_ops, draw_xfbin_list,
                     matrix_prop_group, IntPropertyGroup, StringPropertyGroup)


class SpringGroupsPropertyGroup(PropertyGroup):

    def update_count(self, context):
        extra = self.bone_count - len(self.flags)
        if extra > 0:
            for _ in range(extra):
                self.flags.add()
    
    
    def spring_bone_update(self, context):
        armature_obj = ''
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.xfbin_clump_data.path == context.object.xfbin_dynamics_data.path:
                armature_obj = obj
        if armature_obj != '':
            for i, b in enumerate(armature_obj.data.bones):
                if b.name == self.bone_spring:
                    self.bone_index = i
                    self.name = f'Spring Group [{b.name}]'
                    self.bone_count = len(b.children_recursive) + 1
    

    bone_index: IntProperty(
        name='Bone Index',
        #update= spring_index_update
    )

    bone_count: IntProperty(
        name='Bones Count',
        update= update_count
    )

    dyn1: FloatProperty(
        name='Bounciness',
    )

    dyn2: FloatProperty(
        name='Elasticity',
    )

    dyn3: FloatProperty(
        name='Stiffness',
    )

    dyn4: FloatProperty(
        name='Movement',
    )
    flags: CollectionProperty(
        type = IntPropertyGroup,
        name='Bone flag',
    )

    bone_spring: StringProperty(
        name= 'Bone',
        update= spring_bone_update
    )
    
    spring_group_index: IntProperty(
        name= 'Spring Group Index'
    )
    def update_name(self):
        self.name = 'Spring Group'

    def init_data(self, sgroup: Dynamics1):
        self.bone_index = sgroup.coord_index
        self.bone_count = sgroup.BonesCount
        self.dyn1 = sgroup.Bounciness
        self.dyn2 = sgroup.Elasticity
        self.dyn3 = sgroup.Stiffness
        self.dyn4 = sgroup.Movement
        self.spring_group_index = 0
        

        self.flags.clear()
        for flag in sgroup.shorts:
            f = self.flags.add()
            f.value = flag
class CollisionSpheresPropertyGroup(PropertyGroup):

    def update_count(self, context):
        extra = self.attached_count - len(self.attached_groups)
        if extra > 0:
            for _ in range(extra):
                self.attached_groups.add()
    

    def bone_list(self, context):
        bones = []

        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.xfbin_clump_data.path == context.object.xfbin_dynamics_data.path:
                for b in obj.data.bones:
                    bonename = (b.name, b.name, '')
                    bones.append(bonename)
        return bones


    def collision_bone_update(self, context):
        armature_obj = ''
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.xfbin_clump_data.path == context.object.xfbin_dynamics_data.path:
                armature_obj = obj
        if armature_obj != '':
            for i, b in enumerate(armature_obj.data.bones):
                if b.name == self.bone_collision:
                    self.bone_index = i
                    self.name = f'Collision Group [{b.name}]'

    offset_x: FloatProperty(
        name='X Offset',
    )

    offset_y: FloatProperty(
        name='Y Offset',
    )

    offset_z: FloatProperty(
        name='Z Offset',
    )

    scale_x: FloatProperty(
        name='X Scale',
    )

    scale_y: FloatProperty(
        name='Y Scale',
    )

    scale_z: FloatProperty(
        name='Z Scale',
    )

    bone_index: IntProperty(
    name='Bone Index',
    #update= collision_index_update
    )

    attach_groups: BoolProperty(
        name='Attach Spring Groups',
    )

    attached_count: IntProperty(
        name='Attached Spring Groups Count',
        update= update_count,
        default= 0
    )

    attached_groups: CollectionProperty(
        type = StringPropertyGroup,
        name='Attached Spring Groups',
    )

    '''bone_list: EnumProperty(
        items= bone_list,
        name= 'Test'
    )'''

    bone_collision: StringProperty(
        name= 'Bone',
        update= collision_bone_update
    )

    sg_list: CollectionProperty(
        type= StringPropertyGroup,
    )

    def update_name(self):
        self.name = 'Collision Group'

        

    def init_data(self, colsphere: Dynamics2):
        #offset values
        self.offset_x = colsphere.offset_x
        self.offset_y = colsphere.offset_y
        self.offset_z = colsphere.offset_z
        #scale values
        self.scale_x = colsphere.scale_x
        self.scale_y = colsphere.scale_y
        self.scale_z = colsphere.scale_z
        #rest of the values
        self.bone_index = colsphere.coord_index
        self.attach_groups = colsphere.attach_groups
        #attach_groups flag works as a bool value, but I might be wrong
        if self.attach_groups == 0:
            self.attach_groups = False
        elif self.attach_groups == 1:
            self.attach_groups = True
        #attached spring groups
        self.attached_count = colsphere.attached_groups_count
        self.attached_groups.clear()
        for group in colsphere.attached_groups:
            g = self.attached_groups.add()
            g.value = str(group)
        
        for sp in bpy.context.object.xfbin_dynamics_data.spring_groups:
            g = self.sg_list.add()
            g.value = sp.name

class DynamicsPropertyGroup(PropertyGroup):

    path: StringProperty(
        name='Chunk Path',
        description='',
    )

    clump_name: StringProperty(
        name='Clump Name',
    )

    sg_count: IntProperty(
        name='Spring Groups Count',
    )

    cs_count: IntProperty(
        name='Collision Spheres Count',
    )

    spring_groups: CollectionProperty(
        type=SpringGroupsPropertyGroup,
    )

    sg_index: IntProperty()

    collision_spheres: CollectionProperty(
        type=CollisionSpheresPropertyGroup,
    )

    cs_index: IntProperty()

    name: StringProperty(
    )

    def bonename(self, index, clump):
        return bpy.data.objects[f'{clump} [C]'].data.bones[index].name

    def init_data(self, dynamics: NuccChunkDynamics):
        self.path = dynamics.filePath

        # Set the properties
        self.name = self.clump_name = dynamics.clump_chunk.name
        print(dynamics.clump_chunk)

        self.sg_count = dynamics.SPGroupCount
        self.cs_count = dynamics.ColSphereCount
        
        indices = []
        for g in dynamics.SPGroup:
            indices.append(g.coord_index)

        # Add spring groups
        self.spring_groups.clear()
        for sgroup in dynamics.SPGroup:
            s: SpringGroupsPropertyGroup = self.spring_groups.add()
            s.init_data(sgroup)
            s.name = f'Spring Group [{self.bonename(sgroup.coord_index, self.clump_name)}]'
            s.bone_spring = self.bonename(sgroup.coord_index, self.clump_name)
            for i, index in enumerate(sorted(indices)):
                if index == sgroup.coord_index:
                    s.spring_group_index = i

        
        # Add collision groups
        self.collision_spheres.clear()
        for colsphere in dynamics.ColSphere:
            c: CollisionSpheresPropertyGroup = self.collision_spheres.add()
            c.init_data(colsphere)
            c.name = f'Collision Group [{self.bonename(colsphere.coord_index, self.clump_name)}]'
            c.bone_collision = self.bonename(colsphere.coord_index, self.clump_name)
        
        
            
        

class DynamicsPropertyPanel(Panel):

    bl_idname = 'OBJECT_PT_xfbin_dynamics'
    bl_label = '[XFBIN] Dynamics Properties'

    bl_space_type = 'PROPERTIES'
    bl_context = 'object'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'EMPTY' and obj.parent is None and obj.name.startswith(XFBIN_DYNAMICS_OBJ)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        data: DynamicsPropertyGroup = obj.xfbin_dynamics_data

        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.xfbin_clump_data.path == context.object.xfbin_dynamics_data.path:
                armature_obj = obj
        
        def getindex(bone):
            boneindex = 0
            for i, b in enumerate(armature_obj.data.bones):
                if bone == b.name:
                    boneindex = i
            return boneindex
        draw_copy_paste_ops(layout, 'xfbin_dynamics_data', 'Dynamics Properties')
        
        layout.prop(data, 'clump_name')
        layout.prop(data, 'path')
        layout.operator(update_dynamics.bl_idname)

        box = layout.box()
        row = box.row()
        row.label(text = f'Spring Group Count = {len(context.object.xfbin_dynamics_data.spring_groups)}')
        row.label(text = f'Collision Groups Count = {len(context.object.xfbin_dynamics_data.collision_spheres)}')
        #row.prop(data, 'sg_count')
        #row.prop(data, 'cs_count')


        layout.label(text='Spring Groups')
        draw_xfbin_list(layout, 0, data, f'xfbin_dynamics_data', 'spring_groups', 'sg_index')
        sg_index = data.sg_index


        if data.spring_groups and sg_index >= 0:
            spring_groups: SpringGroupsPropertyGroup = data.spring_groups[sg_index]
            box = layout.box()
            row = box.row()
            row.prop_search(spring_groups, 'bone_spring', armature_obj.data, 'bones')
            row.prop(spring_groups, 'bone_index')
            #row.label(text= f'Bone index = {getindex(spring_groups.bone_spring)}')
            row.prop(spring_groups, 'bone_count')
            #row.label(text= f'Bones Count = {len(armature_obj.data.bones[spring_groups.bone_spring].children_recursive)+ 1}')
            row.prop(spring_groups, 'spring_group_index')
            row = box.row()
            row.prop(spring_groups, 'dyn1')
            row.prop(spring_groups, 'dyn2')
            row.prop(spring_groups, 'dyn3')
            row.prop(spring_groups, 'dyn4')
            matrix_prop_group(box, spring_groups, 'flags', spring_groups.bone_count, 'Bone Flags')

        
        layout.label(text='Collision Spheres')
        draw_xfbin_list(layout, 1, data, f'xfbin_dynamics_data', 'collision_spheres', 'cs_index')
        cs_index = data.cs_index


        if data.collision_spheres and sg_index >= 0:
            collision_spheres: CollisionSpheresPropertyGroup = data.collision_spheres[cs_index]
            box = layout.box()
            row = box.row()
            row.prop_search(collision_spheres, 'bone_collision', armature_obj.data, 'bones')
            row.prop(collision_spheres, 'bone_index')
            #row.label(text= f'Bone index = {getindex(collision_spheres.bone_collision)}')
            row.prop(collision_spheres, 'attach_groups')
            row = box.row()
            row.prop(collision_spheres, 'offset_x')
            row.prop(collision_spheres, 'offset_y')
            row.prop(collision_spheres, 'offset_z')
            row = box.row()
            row.prop(collision_spheres, 'scale_x')
            row.prop(collision_spheres, 'scale_y')
            row.prop(collision_spheres, 'scale_z')

            if collision_spheres.attach_groups == True:
                row = box.row()
                row.prop(collision_spheres, 'attached_count')
                row.operator(index_to_string.bl_idname)
                matrix_prop_group(box, collision_spheres, 'attached_groups', collision_spheres.attached_count, 'Attached Spring Groups')


class update_dynamics(bpy.types.Operator):
    bl_idname = "object.update_dynamics"
    bl_label = "Update spring and collision bones"
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'EMPTY' and obj.parent is None and obj.name.startswith(XFBIN_DYNAMICS_OBJ)
    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.xfbin_clump_data.path == context.object.xfbin_dynamics_data.path:
                armature_obj = obj
        
        #find dynamics objects
        dyn_objs = [o for o in bpy.data.objects if o.name.startswith(XFBIN_DYNAMICS_OBJ)]

        def update(dynamics_object):
            #update spring groups
            indices = []
            for sp in dynamics_object.xfbin_dynamics_data.spring_groups:
                indices.append(sp.bone_index) #add bone indices to a list to be used later
                #check if the bone
                if sp.bone_spring not in armature_obj.data.bones:
                        self.report(
                        {'WARNING'}, f'Spring Group "{sp.bone_spring}" Could not be found in "{armature_obj.name}". Please remove it')
                #update bone index, count and name
                for i, b in enumerate(armature_obj.data.bones):
                    if sp.bone_spring in armature_obj.data.bones and sp.bone_spring == b.name:
                        sp.bone_index = i
                        sp.bone_count = len(b.children_recursive) + 1
                        sp.name = f'Spring Group [{b.name}]'
            
            #update the index of the spring group
            for i, index in enumerate(sorted(indices)):
                for sp in dynamics_object.xfbin_dynamics_data.spring_groups:
                    if sp.bone_index == index:
                        sp.spring_group_index = i
            print(sorted(indices))

            
            #update collision groups
            for col in dynamics_object.xfbin_dynamics_data.collision_spheres:
                if col.bone_collision not in armature_obj.data.bones:
                    self.report(
                        {'WARNING'}, f'Spring Group "{col.bone_collision}" Could not be found in "{armature_obj.name}". Please remove it')
                for i, b in enumerate(armature_obj.data.bones):
                    if col.bone_collision in armature_obj.data.bones and col.bone_collision == b.name:
                        col.bone_index = i
                        col.name = f'Collision Group [{b.name}]'
        

        #try to only update one dynamics object
        if len(dyn_objs) < 1:
            self.report({'WARNING'}, f'There is no dnyamics chunk object in this collection {bpy.context.collection.name}')
        elif context.object in dyn_objs:
            update(bpy.context.object)
        else:
            for dyn in dny_objs:
                update(dyn)
        
        return {'FINISHED'}

class index_to_string(bpy.types.Operator):
    bl_idname = "object.index_to_string"
    bl_label = "Index to String"
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'EMPTY' and obj.parent is None and obj.name.startswith(XFBIN_DYNAMICS_OBJ)
    def execute(self, context):
            #for col in context.object.xfbin_dynamics_data.collision_spheres:
            cs_index = context.object.xfbin_dynamics_data.cs_index
            if context.object.xfbin_dynamics_data.collision_spheres[cs_index].attach_groups == True and context.object.xfbin_dynamics_data.collision_spheres[cs_index].attached_count > 0:
                for c in context.object.xfbin_dynamics_data.collision_spheres[cs_index].attached_groups:
                    for sp in context.object.xfbin_dynamics_data.spring_groups:
                        if c.value == str(sp.spring_group_index):
                            c.value = sp.name
            return {'FINISHED'}

dynamics_chunks_property_groups = (
    SpringGroupsPropertyGroup,
    CollisionSpheresPropertyGroup,
    DynamicsPropertyGroup
)

dynamics_chunks_classes = (
    *dynamics_chunks_property_groups,
    DynamicsPropertyPanel,
    update_dynamics,
    index_to_string
)