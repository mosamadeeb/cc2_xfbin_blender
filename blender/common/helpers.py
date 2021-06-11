def hex_str_to_int(val: str) -> int:
    return int(val.replace(' ', ''), 16)


def int_to_hex_str(val: int, size: int) -> str:
    # Format the value into a hex string and split it into chunks of 2
    str_val = f'{val:0{size}X}'
    return ' '.join([str_val[i: i + 2] for i in range(0, len(str_val), 2)])


def set_hex_string(data, attr: str, value: str, size: int):
    try:
        val = hex_str_to_int(value)
    except:
        pass
    else:
        data[attr] = int_to_hex_str(val, size)
