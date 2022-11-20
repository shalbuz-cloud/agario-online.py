from . import palette


def get_name(color_id: int) -> str:
    return palette.BASE_COLORS[color_id]['name']


def get_rgb(color_id: int) -> tuple:
    return palette.BASE_COLORS[color_id]['decimal']


def get_hex(color_id: int) -> str:
    return palette.BASE_COLORS[color_id]['hex']
