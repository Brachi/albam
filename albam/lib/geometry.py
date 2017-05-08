
def y_up_to_z_up(x_y_z_tuple):
    x, y, z = x_y_z_tuple
    return x, z * -1, y


def z_up_to_y_up(x_y_z_tuple):
    x, y, z = x_y_z_tuple
    return x, z, y * -1
