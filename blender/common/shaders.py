import bpy

#Materials
def F00A(self, xfbin_mat, matname, nodegrp = 'F00A'):

	material = bpy.data.materials.new(matname)
	material.use_nodes = True
	material.blend_method = 'CLIP'
	material.shadow_method = 'NONE'

	#Remove Unnecessary nodes
	material.node_tree.nodes.remove(material.node_tree.nodes['Principled BSDF'])
	material.node_tree.nodes.remove(material.node_tree.nodes['Material Output'])

	#remove node groups with the same name to prevent issues with min and max values of some nodes
	if bpy.data.node_groups.get(nodegrp):
		bpy.data.node_groups.remove(bpy.data.node_groups.get(nodegrp))

	#Create a new node tree to be used later
	nodetree = bpy.data.node_groups.new(nodegrp, 'ShaderNodeTree')

	#Create a node group to organize nodes and inputs
	nodegroup = material.node_tree.nodes.new('ShaderNodeGroup')
	nodegroup.name = nodegrp
	nodegroup.location = (330, 41)
	#use the node tree we made earlier for our node group
	material.node_tree.nodes[nodegrp].node_tree = nodetree

	#Basic Cel-shader setup
	diffuse_bsdf = nodegroup.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
	diffuse_bsdf.location = (-393, 105)

	shader_rgb = nodegroup.node_tree.nodes.new('ShaderNodeShaderToRGB')
	shader_rgb.location = (-193, 156)

	math_greater = nodegroup.node_tree.nodes.new('ShaderNodeMath')
	math_greater.location = (2, 175)
	math_greater.operation = 'GREATER_THAN'
	math_greater.inputs[1].default_value = 0.15

	lighten = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	lighten.location = (192, 134)
	lighten.blend_type = 'LIGHTEN'
	lighten.inputs[0].default_value = 1

	multiply = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	multiply.location = (407, 118)
	multiply.blend_type = 'MULTIPLY'
	multiply.inputs[0].default_value = 1

	transparent = nodegroup.node_tree.nodes.new('ShaderNodeBsdfTransparent')

	mix_shader = nodegroup.node_tree.nodes.new('ShaderNodeMixShader')

	group_input = nodegroup.node_tree.nodes.new('NodeGroupInput')
	group_input.location = (-126, -140)
	nodegroup.inputs.new('NodeSocketColor','Texture')
	nodegroup.inputs.new('NodeSocketColor','Alpha')

	group_output = nodegroup.node_tree.nodes.new('NodeGroupOutput')
	group_output.location = (638, 74)
	nodegroup.outputs.new('NodeSocketShader','Out')

	tex1 = material.node_tree.nodes.new('ShaderNodeTexImage')
	tex1.location = (-27, -23)
	tex1.name = 'F00A TEX'

	output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
	output.location = (603, 85)

	#Link nodes
	nodegroup.node_tree.links.new(diffuse_bsdf.outputs['BSDF'], shader_rgb.inputs['Shader'])

	nodegroup.node_tree.links.new(shader_rgb.outputs['Color'], math_greater.inputs[0])

	nodegroup.node_tree.links.new(math_greater.outputs[0], lighten.inputs[1])

	nodegroup.node_tree.links.new(lighten.outputs[0], multiply.inputs[1])

	nodegroup.node_tree.links.new(multiply.outputs[0], mix_shader.inputs[2])

	nodegroup.node_tree.links.new(transparent.outputs[0], mix_shader.inputs[1])

	nodegroup.node_tree.links.new(mix_shader.outputs[0], group_output.inputs[0])

	nodegroup.node_tree.links.new(group_input.outputs[0], multiply.inputs[2])
	nodegroup.node_tree.links.new(group_input.outputs['Alpha'], mix_shader.inputs[0])

	material.node_tree.links.new(tex1.outputs[0], nodegroup.inputs['Texture'])
	material.node_tree.links.new(tex1.outputs[1], nodegroup.inputs[1])


	material.node_tree.links.new(nodegroup.outputs[0], output.inputs[0])
	
	if xfbin_mat.texture_groups and xfbin_mat.texture_groups[0].textures:
		image_name = xfbin_mat.texture_groups[0].textures[0].texture
		tex1.image = bpy.data.images.get(image_name)

	return material

def _02_F00A(self, xfbin_mat, matname, nodegrp = '02F00A'):

	material = bpy.data.materials.new(matname)
	material.use_nodes = True
	material.blend_method = 'CLIP'
	material.shadow_method = 'NONE'

	#Remove Unnecessary nodes
	material.node_tree.nodes.remove(material.node_tree.nodes['Principled BSDF'])
	material.node_tree.nodes.remove(material.node_tree.nodes['Material Output'])

	#remove node groups with the same name to prevent issues with min and max values of some nodes
	#for node in bpy.data.node_groups:
	if bpy.data.node_groups.get(nodegrp):
		bpy.data.node_groups.remove(bpy.data.node_groups.get(nodegrp))

	#Create a new node tree to be used later
	nodetree = bpy.data.node_groups.new(nodegrp, 'ShaderNodeTree')

	#Create a node group to organize nodes and inputs
	nodegroup = material.node_tree.nodes.new('ShaderNodeGroup')
	nodegroup.name = nodegrp
	nodegroup.location = (330, 41)
	#use the node tree we made earlier for our node group
	material.node_tree.nodes[nodegrp].node_tree = nodetree

	#Basic Cel-shader setup
	diffuse_bsdf = nodegroup.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
	diffuse_bsdf.location = (-393, 105)

	shader_rgb = nodegroup.node_tree.nodes.new('ShaderNodeShaderToRGB')
	shader_rgb.location = (-193, 156)

	math_greater = nodegroup.node_tree.nodes.new('ShaderNodeMath')
	math_greater.location = (2, 175)
	math_greater.operation = 'GREATER_THAN'
	math_greater.inputs[1].default_value = 0.15

	lighten = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	lighten.location = (192, 134)
	lighten.blend_type = 'LIGHTEN'
	lighten.inputs[0].default_value = 1

	multiply1 = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	multiply1.location = (407, 118)
	multiply1.blend_type = 'MULTIPLY'
	multiply1.inputs[0].default_value = 1

	mix1 = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	mix1.location = (407, 158)
	mix1.blend_type = 'MIX'
	mix1.inputs[0].default_value = 1

	#This will be used for texture 2 visibility
	mix2 = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	mix2.location = (407, 0)
	mix2.blend_type = 'MIX'
	mix2.inputs[1].default_value = (0, 0, 0, 1)

	transparent = nodegroup.node_tree.nodes.new('ShaderNodeBsdfTransparent')

	mix_shader = nodegroup.node_tree.nodes.new('ShaderNodeMixShader')

	group_input = nodegroup.node_tree.nodes.new('NodeGroupInput')
	group_input.location = (-126, -140)
	nodegroup.inputs.new('NodeSocketColor','Texture1')
	nodegroup.inputs.new('NodeSocketColor','Texture2')
	nodegroup.inputs.new('NodeSocketColor','Alpha1')
	nodegroup.inputs.new('NodeSocketColor','Alpha2')
	nodegroup.inputs.new('NodeSocketFloat','Texture2 Visibility')
	bpy.data.node_groups[nodegroup.name].inputs[4].min_value = 0.0
	bpy.data.node_groups[nodegroup.name].inputs[4].max_value = 1.0
	
	nodegroup.inputs[4].default_value = 1.0


	group_output = nodegroup.node_tree.nodes.new('NodeGroupOutput')
	group_output.location = (638, 74)
	nodegroup.outputs.new('NodeSocketShader','Out')

	uv1 = material.node_tree.nodes.new('ShaderNodeUVMap')
	uv1.location = (-77, -23)
	uv1.uv_map = 'UV_0'

	uv2 = material.node_tree.nodes.new('ShaderNodeUVMap')
	uv2.location = (-77, -23)
	uv2.uv_map = 'UV_1'

	tex1 = material.node_tree.nodes.new('ShaderNodeTexImage')
	tex1.location = (-27, -23)
	tex1.name = 'Texture1'

	tex2 = material.node_tree.nodes.new('ShaderNodeTexImage')
	tex2.location = (-27, -43)
	tex2.name = 'Texture2'

	output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
	output.location = (603, 85)

	#Link nodes
	nodegroup.node_tree.links.new(diffuse_bsdf.outputs['BSDF'], shader_rgb.inputs['Shader'])

	nodegroup.node_tree.links.new(shader_rgb.outputs['Color'], math_greater.inputs[0])

	nodegroup.node_tree.links.new(math_greater.outputs[0], lighten.inputs[1])

	nodegroup.node_tree.links.new(lighten.outputs[0], multiply1.inputs[1])

	nodegroup.node_tree.links.new(mix1.outputs[0], multiply1.inputs[2])

	nodegroup.node_tree.links.new(group_input.outputs[0], mix1.inputs[1])

	nodegroup.node_tree.links.new(group_input.outputs[1], mix1.inputs[2])

	nodegroup.node_tree.links.new(group_input.outputs[2], mix_shader.inputs[0])

	nodegroup.node_tree.links.new(group_input.outputs[3], mix2.inputs[2])

	nodegroup.node_tree.links.new(group_input.outputs[4], mix2.inputs[0])

	nodegroup.node_tree.links.new(mix2.outputs[0], mix1.inputs[0])

	nodegroup.node_tree.links.new(transparent.outputs[0], mix_shader.inputs[1])

	nodegroup.node_tree.links.new(multiply1.outputs[0], mix_shader.inputs[2])

	nodegroup.node_tree.links.new(mix_shader.outputs[0], group_output.inputs[0])

	material.node_tree.links.new(uv1.outputs[0], tex1.inputs[0])
	material.node_tree.links.new(tex1.outputs[0], nodegroup.inputs['Texture1'])
	material.node_tree.links.new(tex1.outputs[1], nodegroup.inputs['Alpha1'])

	material.node_tree.links.new(uv2.outputs[0], tex2.inputs[0])
	material.node_tree.links.new(tex2.outputs[0], nodegroup.inputs['Texture2'])
	material.node_tree.links.new(tex2.outputs[1], nodegroup.inputs['Alpha2'])

	material.node_tree.links.new(nodegroup.outputs[0], output.inputs[0])
	
	if xfbin_mat.texture_groups and xfbin_mat.texture_groups[0].textures:
		image_name = xfbin_mat.texture_groups[0].textures[0].texture
		tex1.image = bpy.data.images.get(image_name)
		image_name2 = xfbin_mat.texture_groups[0].textures[1].texture
		tex2.image = bpy.data.images.get(image_name2)

	return material

def _01_F003(self, xfbin_mat, matname, nodegrp = '01F003'):

	material = bpy.data.materials.new(matname)
	material.use_nodes = True
	material.blend_method = 'CLIP'
	material.shadow_method = 'NONE'

	#Remove Unnecessary nodes
	material.node_tree.nodes.remove(material.node_tree.nodes['Principled BSDF'])
	material.node_tree.nodes.remove(material.node_tree.nodes['Material Output'])

	#remove node groups with the same name to prevent issues with min and max values of some nodes
	if bpy.data.node_groups.get(nodegrp):
		bpy.data.node_groups.remove(bpy.data.node_groups.get(nodegrp))

	#Create a new node tree to be used later
	nodetree = bpy.data.node_groups.new(nodegrp, 'ShaderNodeTree')

	#Create a node group to organize nodes and inputs
	nodegroup = material.node_tree.nodes.new('ShaderNodeGroup')
	nodegroup.name = nodegrp
	nodegroup.location = (721, 611)
	#use the node tree we made earlier for our node group
	material.node_tree.nodes[nodegrp].node_tree = nodetree

	#Nodes
	diffuse_bsdf = nodegroup.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
	diffuse_bsdf.location = (-519, 304)

	shader_rgb = nodegroup.node_tree.nodes.new('ShaderNodeShaderToRGB')
	shader_rgb.location = (-327, 305)

	math_greater = nodegroup.node_tree.nodes.new('ShaderNodeMath')
	math_greater.location = (-163, 320)
	math_greater.operation = 'GREATER_THAN'
	math_greater.inputs[1].default_value = 0.00

	lighten = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	lighten.location = (47, 300)
	lighten.blend_type = 'LIGHTEN'
	lighten.inputs[0].default_value = 1
	lighten.inputs[2].default_value = (0.2,0.2,0.2,1)

	multiply1 = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	multiply1.location = (256, 131)
	multiply1.blend_type = 'MULTIPLY'
	multiply1.inputs[0].default_value = 1

	multiply2 = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	multiply2.location = (256, 131)
	multiply2.blend_type = 'MULTIPLY'
	multiply2.inputs[0].default_value = 1

	transparent = nodegroup.node_tree.nodes.new('ShaderNodeBsdfTransparent')
	transparent.location = (264, -261)

	mix_shader = nodegroup.node_tree.nodes.new('ShaderNodeMixShader')
	mix_shader.location = (696, -113)

	group_input = nodegroup.node_tree.nodes.new('NodeGroupInput')
	group_input.location = (-56, -112)
	nodegroup.inputs.new('NodeSocketColor','Diffuse Texture')
	nodegroup.inputs.new('NodeSocketColor','Alpha')
	nodegroup.inputs.new('NodeSocketColor','Vertex Colors')

	group_output = nodegroup.node_tree.nodes.new('NodeGroupOutput')
	group_output.location = (886, 4)
	nodegroup.outputs.new('NodeSocketShader','Out')

	vcol = material.node_tree.nodes.new('ShaderNodeVertexColor')

	uv1 = material.node_tree.nodes.new('ShaderNodeUVMap')
	uv1.location = (-84, -552)
	uv1.uv_map = 'UV_0'

	tex1 = material.node_tree.nodes.new('ShaderNodeTexImage')
	tex1.location = (174, 720)
	tex1.name = 'Diffuse'

	output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
	output.location = (1091, 520)

	#Link nodes
	nodegroup.node_tree.links.new(diffuse_bsdf.outputs['BSDF'], shader_rgb.inputs['Shader'])

	nodegroup.node_tree.links.new(shader_rgb.outputs['Color'], math_greater.inputs[0])

	nodegroup.node_tree.links.new(math_greater.outputs[0], lighten.inputs[1])

	nodegroup.node_tree.links.new(lighten.outputs[0], multiply1.inputs[1])

	nodegroup.node_tree.links.new(multiply1.outputs[0], multiply2.inputs[1])

	nodegroup.node_tree.links.new(multiply2.outputs[0], mix_shader.inputs[2])

	nodegroup.node_tree.links.new(transparent.outputs[0], mix_shader.inputs[1])

	nodegroup.node_tree.links.new(mix_shader.outputs[0], group_output.inputs[0])

	nodegroup.node_tree.links.new(group_input.outputs[0], multiply1.inputs[2])
	nodegroup.node_tree.links.new(group_input.outputs[1], mix_shader.inputs[0])
	nodegroup.node_tree.links.new(group_input.outputs[2], multiply2.inputs[2])

	material.node_tree.links.new(vcol.outputs[0], nodegroup.inputs[2])

	material.node_tree.links.new(uv1.outputs[0], tex1.inputs[0])
	material.node_tree.links.new(tex1.outputs[0], nodegroup.inputs[0])
	material.node_tree.links.new(tex1.outputs[1], nodegroup.inputs[1])

	material.node_tree.links.new(nodegroup.outputs[0], output.inputs[0])

	if xfbin_mat.texture_groups and xfbin_mat.texture_groups[0].textures:
		image_name = xfbin_mat.texture_groups[0].textures[0].texture
		tex1.image = bpy.data.images.get(image_name)

	return material

def _05_F00D(self, xfbin_mat, matname, nodegrp = '05F00D'):

	material = bpy.data.materials.new(matname)
	material.use_nodes = True
	material.blend_method = 'CLIP'
	material.shadow_method = 'NONE'

	#Remove Unnecessary nodes
	material.node_tree.nodes.remove(material.node_tree.nodes['Principled BSDF'])
	material.node_tree.nodes.remove(material.node_tree.nodes['Material Output'])

	#remove node groups with the same name to prevent issues with min and max values of some nodes
	if bpy.data.node_groups.get(nodegrp):
		bpy.data.node_groups.remove(bpy.data.node_groups.get(nodegrp))

	#Create a new node tree to be used later
	nodetree = bpy.data.node_groups.new(nodegrp, 'ShaderNodeTree')

	#Create a node group to organize nodes and inputs
	nodegroup = material.node_tree.nodes.new('ShaderNodeGroup')
	nodegroup.name = nodegrp
	nodegroup.location = (721, 611)
	#use the node tree we made earlier for our node group
	material.node_tree.nodes[nodegrp].node_tree = nodetree

	#Nodes
	normal = nodegroup.node_tree.nodes.new('ShaderNodeNormal')
	normal.location = (-696, 350)

	diffuse_bsdf = nodegroup.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
	diffuse_bsdf.location = (-519, 304)

	shader_rgb = nodegroup.node_tree.nodes.new('ShaderNodeShaderToRGB')
	shader_rgb.location = (-327, 305)

	math_greater = nodegroup.node_tree.nodes.new('ShaderNodeMath')
	math_greater.location = (-163, 320)
	math_greater.operation = 'GREATER_THAN'
	math_greater.inputs[1].default_value = 0.06

	lighten = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	lighten.location = (47, 300)
	lighten.blend_type = 'LIGHTEN'
	lighten.inputs[0].default_value = 1
	lighten.inputs[2].default_value = (0.2,0.2,0.2,1)

	multiply1 = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	multiply1.location = (256, 131)
	multiply1.blend_type = 'MULTIPLY'
	multiply1.inputs[0].default_value = 1

	multiply2 = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	multiply2.location = (476, 81)
	multiply2.blend_type = 'MULTIPLY'
	multiply2.inputs[0].default_value = 1

	transparent = nodegroup.node_tree.nodes.new('ShaderNodeBsdfTransparent')
	transparent.location = (264, -261)

	mix_shader = nodegroup.node_tree.nodes.new('ShaderNodeMixShader')
	mix_shader.location = (696, -113)

	group_input = nodegroup.node_tree.nodes.new('NodeGroupInput')
	group_input.location = (-56, -112)
	nodegroup.inputs.new('NodeSocketColor','Diffuse Texture')
	nodegroup.inputs.new('NodeSocketColor','Shadow Texture')
	nodegroup.inputs.new('NodeSocketColor','Alpha')

	group_output = nodegroup.node_tree.nodes.new('NodeGroupOutput')
	group_output.location = (886, 4)
	nodegroup.outputs.new('NodeSocketShader','Out')

	uv1 = material.node_tree.nodes.new('ShaderNodeUVMap')
	uv1.location = (-84, -552)
	uv1.uv_map = 'UV_0'

	uv2 = material.node_tree.nodes.new('ShaderNodeUVMap')
	uv2.location = (-78, -308)
	uv2.uv_map = 'UV_1'

	tex1 = material.node_tree.nodes.new('ShaderNodeTexImage')
	tex1.location = (174, 720)
	tex1.name = 'Diffuse'

	tex2 = material.node_tree.nodes.new('ShaderNodeTexImage')
	tex2.location = (178, 420)
	tex2.name = 'Shadow'

	output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
	output.location = (1091, 520)

	#Link nodes
	nodegroup.node_tree.links.new(normal.outputs[0], diffuse_bsdf.inputs[2])

	nodegroup.node_tree.links.new(diffuse_bsdf.outputs['BSDF'], shader_rgb.inputs['Shader'])

	nodegroup.node_tree.links.new(shader_rgb.outputs['Color'], math_greater.inputs[0])

	nodegroup.node_tree.links.new(math_greater.outputs[0], lighten.inputs[1])

	nodegroup.node_tree.links.new(lighten.outputs[0], multiply1.inputs[1])

	nodegroup.node_tree.links.new(multiply1.outputs[0], multiply2.inputs[1])

	nodegroup.node_tree.links.new(multiply2.outputs[0], mix_shader.inputs[2])

	nodegroup.node_tree.links.new(transparent.outputs[0], mix_shader.inputs[1])

	nodegroup.node_tree.links.new(mix_shader.outputs[0], group_output.inputs[0])

	nodegroup.node_tree.links.new(group_input.outputs[0], multiply1.inputs[2])
	nodegroup.node_tree.links.new(group_input.outputs[1], multiply2.inputs[2])
	nodegroup.node_tree.links.new(group_input.outputs[2], mix_shader.inputs[0])

	material.node_tree.links.new(uv1.outputs[0], tex1.inputs[0])
	material.node_tree.links.new(tex1.outputs[0], nodegroup.inputs[0])
	material.node_tree.links.new(tex1.outputs[1], nodegroup.inputs[2])

	material.node_tree.links.new(uv2.outputs[0], tex2.inputs[0])
	material.node_tree.links.new(tex2.outputs[0], nodegroup.inputs[1])



	material.node_tree.links.new(nodegroup.outputs[0], output.inputs[0])

	if xfbin_mat.texture_groups and xfbin_mat.texture_groups[0].textures:
		image_name = xfbin_mat.texture_groups[0].textures[0].texture
		tex1.image = bpy.data.images.get(image_name)
		image_name2 = xfbin_mat.texture_groups[0].textures[1].texture
		tex2.image = bpy.data.images.get(image_name2)

	return material

def _05_F002(self, xfbin_mat, matname, nodegrp = '05F002'):

	material = bpy.data.materials.new(matname)
	material.use_nodes = True
	material.blend_method = 'CLIP'
	material.shadow_method = 'NONE'

	#Remove Unnecessary nodes
	material.node_tree.nodes.remove(material.node_tree.nodes['Principled BSDF'])
	material.node_tree.nodes.remove(material.node_tree.nodes['Material Output'])

	#remove node groups with the same name to prevent issues with min and max values of some nodes
	if bpy.data.node_groups.get(nodegrp):
		bpy.data.node_groups.remove(bpy.data.node_groups.get(nodegrp))

	#Create a new node tree to be used later
	nodetree = bpy.data.node_groups.new(nodegrp, 'ShaderNodeTree')

	#Create a node group to organize nodes and inputs
	nodegroup = material.node_tree.nodes.new('ShaderNodeGroup')
	nodegroup.name = nodegrp
	nodegroup.location = (721, 611)
	#use the node tree we made earlier for our node group
	material.node_tree.nodes[nodegrp].node_tree = nodetree

	#Nodes

	multiply1 = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	multiply1.location = (256, 131)
	multiply1.blend_type = 'MULTIPLY'
	multiply1.inputs[0].default_value = 1


	transparent = nodegroup.node_tree.nodes.new('ShaderNodeBsdfTransparent')
	transparent.location = (264, -261)

	mix_shader = nodegroup.node_tree.nodes.new('ShaderNodeMixShader')
	mix_shader.location = (696, -113)

	group_input = nodegroup.node_tree.nodes.new('NodeGroupInput')
	group_input.location = (-56, -112)
	nodegroup.inputs.new('NodeSocketColor','Diffuse Texture')
	nodegroup.inputs.new('NodeSocketColor','Alpha')
	nodegroup.inputs.new('NodeSocketColor','Vertex Colors')

	group_output = nodegroup.node_tree.nodes.new('NodeGroupOutput')
	group_output.location = (886, 4)
	nodegroup.outputs.new('NodeSocketShader','Out')

	vcol = material.node_tree.nodes.new('ShaderNodeVertexColor')

	uv1 = material.node_tree.nodes.new('ShaderNodeUVMap')
	uv1.location = (-84, -552)
	uv1.uv_map = 'UV_0'

	tex1 = material.node_tree.nodes.new('ShaderNodeTexImage')
	tex1.location = (174, 720)
	tex1.name = 'Diffuse'

	output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
	output.location = (1091, 520)

	#Link nodes
	nodegroup.node_tree.links.new(transparent.outputs[0], mix_shader.inputs[1])

	nodegroup.node_tree.links.new(mix_shader.outputs[0], group_output.inputs[0])

	nodegroup.node_tree.links.new(group_input.outputs[0], multiply1.inputs[1])

	nodegroup.node_tree.links.new(group_input.outputs[2], multiply1.inputs[2])

	nodegroup.node_tree.links.new(group_input.outputs[1], mix_shader.inputs[0])

	nodegroup.node_tree.links.new(multiply1.outputs[0], mix_shader.inputs[2])

	material.node_tree.links.new(vcol.outputs[0], nodegroup.inputs[2])

	material.node_tree.links.new(uv1.outputs[0], tex1.inputs[0])
	material.node_tree.links.new(tex1.outputs[0], nodegroup.inputs[0])
	material.node_tree.links.new(tex1.outputs[1], nodegroup.inputs[1])

	material.node_tree.links.new(nodegroup.outputs[0], output.inputs[0])

	if xfbin_mat.texture_groups and xfbin_mat.texture_groups[0].textures:
		image_name = xfbin_mat.texture_groups[0].textures[0].texture
		tex1.image = bpy.data.images.get(image_name)

	return material

def _07_F002(self, xfbin_mat, matname, nodegrp = '07F002'):

	material = bpy.data.materials.new(matname)
	material.use_nodes = True
	material.blend_method = 'CLIP'
	material.shadow_method = 'NONE'

	#Remove Unnecessary nodes
	material.node_tree.nodes.remove(material.node_tree.nodes['Principled BSDF'])
	material.node_tree.nodes.remove(material.node_tree.nodes['Material Output'])

	#remove node groups with the same name to prevent issues with min and max values of some nodes
	if bpy.data.node_groups.get(nodegrp):
		bpy.data.node_groups.remove(bpy.data.node_groups.get(nodegrp))

	#Create a new node tree to be used later
	nodetree = bpy.data.node_groups.new(nodegrp, 'ShaderNodeTree')

	#Create a node group to organize nodes and inputs
	nodegroup = material.node_tree.nodes.new('ShaderNodeGroup')
	nodegroup.name = nodegrp
	nodegroup.location = (721, 611)
	#use the node tree we made earlier for our node group
	material.node_tree.nodes[nodegrp].node_tree = nodetree

	#Nodes

	multiply1 = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	multiply1.location = (256, 131)
	multiply1.blend_type = 'MULTIPLY'
	multiply1.inputs[0].default_value = 1

	multiply2 = nodegroup.node_tree.nodes.new('ShaderNodeMixRGB')
	multiply2.location = (256, 131)
	multiply2.blend_type = 'MULTIPLY'
	multiply2.inputs[0].default_value = 1


	transparent = nodegroup.node_tree.nodes.new('ShaderNodeBsdfTransparent')
	transparent.location = (264, -261)

	mix_shader = nodegroup.node_tree.nodes.new('ShaderNodeMixShader')
	mix_shader.location = (696, -113)

	group_input = nodegroup.node_tree.nodes.new('NodeGroupInput')
	group_input.location = (-56, -112)
	nodegroup.inputs.new('NodeSocketColor','Diffuse Texture')
	nodegroup.inputs.new('NodeSocketColor','Shadow Texture')
	nodegroup.inputs.new('NodeSocketColor','Alpha')
	nodegroup.inputs.new('NodeSocketColor','Tweak Colors')
	material.node_tree.nodes[nodegrp].inputs['Tweak Colors'].default_value = (1,1,1,1)

	group_output = nodegroup.node_tree.nodes.new('NodeGroupOutput')
	group_output.location = (886, 4)
	nodegroup.outputs.new('NodeSocketShader','Out')

	uv1 = material.node_tree.nodes.new('ShaderNodeUVMap')
	uv1.location = (-84, -552)
	uv1.uv_map = 'UV_0'

	tex1 = material.node_tree.nodes.new('ShaderNodeTexImage')
	tex1.location = (174, 720)
	tex1.name = 'Diffuse'

	uv2 = material.node_tree.nodes.new('ShaderNodeUVMap')
	uv2.location = (-84, -552)
	uv2.uv_map = 'UV_1'

	tex2 = material.node_tree.nodes.new('ShaderNodeTexImage')
	tex2.location = (174, 720)
	tex2.name = 'Diffuse'


	output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
	output.location = (1091, 520)

	#Link nodes
	nodegroup.node_tree.links.new(transparent.outputs[0], mix_shader.inputs[1])

	nodegroup.node_tree.links.new(mix_shader.outputs[0], group_output.inputs[0])

	nodegroup.node_tree.links.new(group_input.outputs[0], multiply1.inputs[1])

	nodegroup.node_tree.links.new(group_input.outputs[1], multiply1.inputs[2])

	nodegroup.node_tree.links.new(group_input.outputs[2], mix_shader.inputs[0])

	nodegroup.node_tree.links.new(group_input.outputs[3], multiply2.inputs[2])

	nodegroup.node_tree.links.new(multiply1.outputs[0], multiply2.inputs[1])

	nodegroup.node_tree.links.new(multiply2.outputs[0], mix_shader.inputs[2])

	material.node_tree.links.new(uv1.outputs[0], tex1.inputs[0])
	material.node_tree.links.new(tex1.outputs[0], nodegroup.inputs[0])
	material.node_tree.links.new(tex1.outputs[1], nodegroup.inputs[2])

	material.node_tree.links.new(uv2.outputs[0], tex2.inputs[0])
	material.node_tree.links.new(tex2.outputs[0], nodegroup.inputs[1])

	material.node_tree.links.new(nodegroup.outputs[0], output.inputs[0])

	if xfbin_mat.texture_groups and xfbin_mat.texture_groups[0].textures:
		image_name = xfbin_mat.texture_groups[0].textures[0].texture
		tex1.image = bpy.data.images.get(image_name)
		image_name = xfbin_mat.texture_groups[0].textures[1].texture
		tex2.image = bpy.data.images.get(image_name)

	return material


def E002(self, xfbin_mat, matname, nodegrp = 'E002'):

	material = bpy.data.materials.new(matname)
	material.use_nodes = True
	material.blend_method = 'CLIP'
	material.shadow_method = 'CLIP'

	#Remove Unnecessary nodes
	material.node_tree.nodes.remove(material.node_tree.nodes['Principled BSDF'])
	material.node_tree.nodes.remove(material.node_tree.nodes['Material Output'])

	#remove node groups with the same name to prevent issues with min and max values of some nodes
	if bpy.data.node_groups.get(nodegrp):
		bpy.data.node_groups.remove(bpy.data.node_groups.get(nodegrp))

	#Create a new node tree to be used later
	nodetree = bpy.data.node_groups.new(nodegrp, 'ShaderNodeTree')

	#Create a node group to organize nodes and inputs
	nodegroup = material.node_tree.nodes.new('ShaderNodeGroup')
	nodegroup.name = nodegrp
	nodegroup.location = (721, 611)
	#use the node tree we made earlier for our node group
	material.node_tree.nodes[nodegrp].node_tree = nodetree

	#Nodes
	transparent = nodegroup.node_tree.nodes.new('ShaderNodeBsdfTransparent')

	mix_shader = nodegroup.node_tree.nodes.new('ShaderNodeMixShader')

	group_input = nodegroup.node_tree.nodes.new('NodeGroupInput')
	group_input.location = (-56, -112)
	nodegroup.inputs.new('NodeSocketColor','Texture')
	nodegroup.inputs.new('NodeSocketColor','Alpha')

	group_output = nodegroup.node_tree.nodes.new('NodeGroupOutput')
	group_output.location = (886, 4)
	nodegroup.outputs.new('NodeSocketShader','Out')

	uv1 = material.node_tree.nodes.new('ShaderNodeUVMap')
	uv1.location = (-84, -552)
	uv1.uv_map = 'UV_0'

	tex1 = material.node_tree.nodes.new('ShaderNodeTexImage')
	tex1.location = (174, 720)
	tex1.name = 'Diffuse'

	output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
	output.location = (1091, 520)

	#Link nodes
	nodegroup.node_tree.links.new(transparent.outputs[0], mix_shader.inputs[1])

	nodegroup.node_tree.links.new(mix_shader.outputs[0], group_output.inputs[0])

	nodegroup.node_tree.links.new(group_input.outputs[0], mix_shader.inputs[2])

	nodegroup.node_tree.links.new(group_input.outputs[1], mix_shader.inputs[0])

	material.node_tree.links.new(uv1.outputs[0], tex1.inputs[0])
	material.node_tree.links.new(tex1.outputs[0], nodegroup.inputs[0])
	material.node_tree.links.new(tex1.outputs[1], nodegroup.inputs[1])

	material.node_tree.links.new(nodegroup.outputs[0], output.inputs[0])

	if xfbin_mat.texture_groups and xfbin_mat.texture_groups[0].textures:
		image_name = xfbin_mat.texture_groups[0].textures[0].texture
		tex1.image = bpy.data.images.get(image_name)

	return material