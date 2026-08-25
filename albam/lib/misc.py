import colorsys


def chunks(list_, n):
    return [list_[i: i + n] for i in range(0, len(list_), n)]


def number_to_color(flags: int):
    # Knuth hash
    h = (flags * 2654435761) & 0xFFFFFFFF
    hue = h / 2**32
    saturation = 0.45
    value = 0.90
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)

    return (r, g, b, 1.0)
