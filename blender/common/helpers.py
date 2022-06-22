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
