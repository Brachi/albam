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


# Very smartass(?) way to dynamically create a list with 44 colors
class counter():
    def __init__(self):
        self.i = 0

    def count(self):
        self.i += 1
        return self.i


i = counter()


def cycle():
    return [0.4, 0.6, 0.8, 1.0][i.count() % 4]


base_palette = [colorsys.hsv_to_rgb(c / 55, 1.0, cycle()) for c in range(44)]
base_palette = [(i[0], i[1], i[2], 1.0) for i in base_palette]
