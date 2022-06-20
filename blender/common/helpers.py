import bpy, array, struct



XFBIN_TEXTURES_OBJ = '#XFBIN Textures'

XFBIN_DYNAMICS_OBJ = '#XFBIN Dynamics'

def hex_str_to_int(val: str) -> int:
    return int(val.replace(' ', ''), 16)


def int_to_hex_str(val: int, size: int) -> str:
    # Format the value into a hex string and split it into chunks of 2
    str_val = f'{val:0{size*2}X}'
    return ' '.join([str_val[i: i + 2] for i in range(0, len(str_val), 2)])


def format_hex_str(value: str, size: int):
    try:
        val = hex_str_to_int(value)
    except:
        pass
    else:
        return int_to_hex_str(val, size)
    

def image_from_data(image_name: str, width: int, height: int, data: bytes):
    image = bpy.data.images.new(image_name, width, height)

    image.pack(data=data, data_len=len(data))

    image.source = 'FILE'

    return image


def nut2dds(nut: object) -> bytes:
	# Bit masks
	RGB_555 = (0x7C00, 0x3E0, 0x1F, 0x8000)
	RGB_444 = (0xF00, 0xF0, 0xF, 0xF000)
	RGB_565 = (0xF800, 0x7E0, 0x1F, 0x0)
	RGB_888 = (0xFF0000, 0xFF00, 0xFF, 0xFF000000)
    

    # Set the header for the DDS based on the NUT's pixel format
	def set_header(pixel_format):
		if (pixel_format == 0):
			header = BC1_HEADER

		elif (pixel_format == 1):
			header = BC2_HEADER

		elif (pixel_format == 2):
			header = BC3_HEADER

		elif (pixel_format == 6):
			header = B5G5R5A1_HEADER

		elif (pixel_format == 7):
			header = B4G4R4A4_HEADER

		elif (pixel_format == 8):
			header = B5G6R5_HEADER

		elif (pixel_format == 14):
			header = B8G8R8A8_HEADER

		elif (pixel_format == 17):
			header = B8G8R8A8_HEADER
		return header

    
    # Swap endian depending on compression
	def compress_DXTn(pixel_format, header, texture_data):
		if (pixel_format == 0 or pixel_format == 1 or pixel_format == 2):
			return array.array('u', header) + array.array('u', texture_data)	
		
		if (pixel_format == 6 or pixel_format == 7 or pixel_format == 8):
			texture_data = array.array('u', texture_data)
			texture_data.byteswap()
			return array.array('u', header) + texture_data
		
		if (pixel_format == 16 or pixel_format == 14 or pixel_format == 17):
			texture_data = array.array('l', texture_data)
			texture_data.byteswap()
			return array.array('l', header) + texture_data

	
	def structDXT(compression):
		reserved1 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
		return  (b'DDS ', 0x7C, 0x1007, nut.height, nut.width, nut.data_size, 0x0, nut.mipmap_count, *reserved1, 0x20, 0x4, compression, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0)

	def structDXT10(pitch, flags, bit, rgb):
		reserved1 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
		return (b'DDS ', 0x7C, 0x2100F, nut.height, nut.width, pitch, 0x0, nut.mipmap_count, *reserved1, 0x20, flags, 0x0, bit, *rgb, 0x401008, 0x0, 0x0, 0x0, 0x0)


	# String formats used for struct packing
	dxt_fstring = '4sllllllll11ll4sllllllllll' # DXT
	dxt10_fstring  = '4sllllllll11llllLLLLlllll' # DXT10
	
	# DXT Headers
	BC1_HEADER = struct.pack(dxt_fstring, *structDXT(b'DXT1'))
	BC2_HEADER = struct.pack(dxt_fstring, *structDXT(b'DXT3'))
	BC3_HEADER = struct.pack(dxt_fstring, *structDXT(b'DXT5'))

	# DXT10 headers
	B5G5R5A1_HEADER = struct.pack(dxt10_fstring, *structDXT10(0x400, 0x41, 0x10, RGB_555))
	B4G4R4A4_HEADER = struct.pack(dxt10_fstring, *structDXT10(0x400, 0x41, 0x10, RGB_444))
	B5G6R5_HEADER = struct.pack(dxt10_fstring, *structDXT10(0x400, 0x40, 0x10, RGB_565))
	B8G8R8A8_HEADER = struct.pack(dxt10_fstring, *structDXT10(0x800, 0x41, 0x20, RGB_888))
		
	# Create DDS object
	dds_file_object = compress_DXTn(nut.pixel_format, set_header(nut.pixel_format), nut.texture_data)


	return dds_file_object.tobytes()


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
	if bpy.data.node_groups.get(node.name):
		bpy.data.node_groups.remove(bpy.data.node_groups.get(node.name))

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