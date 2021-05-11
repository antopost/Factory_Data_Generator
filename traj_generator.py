import math
import json
import traj_random

# track length (cm)
L = 2851.5
# track width (cm)
W = 1568.5
# camera height (cm)
H = 155
# step length (cm)
S = 4
# turning radius (cm)
R = 330
# camera pitch in deg
P = -30
# set name
map_name = 'map1'


def save_to_file(filename, metadata):
    with open(filename, 'w') as f:
        json.dump(metadata, f, indent=4)


def generate_traj(r, s):
    """
    Generates a camera trajectory depending on the vehicles turning radius step length of camera points in cm
    Assumes that the starting point is at (0,0)
    No randomnes
    r: turning radius
    s: step length
    """
    pi = math.pi
    # increments on turn
    dphi = s / r
    # length and width of straights
    l = L - 2 * r
    w = W - 2 * r
    # entire length of path
    s_tot = 2 * (l + w + r * pi)
    # total number of increments
    n = s_tot / s

    # number of steps at the end of each section
    n1 = l / s
    n2 = n1 + pi * r / (2 * s)
    n3 = n2 + w / s
    n4 = n3 + pi * r / (2 * s)
    n5 = n4 + l / s
    n6 = n5 + pi * r / (2 * s)
    n7 = n6 + w / s

    trajectory = []
    # x and y are flipped for some reason
    # rotation is also totally wack: negative rotation is positive
    for k in range(math.ceil(n1)):
        loc = [k * s + r, 0, H]
        rot = [P, 0, 0]
        trajectory.append(dict(rotation=rot, location=loc))

    for k in range(math.ceil(n1), math.floor(n2)):
        loc_y = - r * (1 - math.cos(dphi * (k - n1)))
        loc_x = l + r * math.sin(dphi * (k - n1)) + r
        rot_z = - math.degrees(dphi * (k - n1))
        loc = [loc_x, loc_y, H]
        rot = [P, rot_z, 0]
        trajectory.append(dict(rotation=rot, location=loc))

    for k in range(math.ceil(n2), math.floor(n3)):
        loc_y = - (k - n2) * s - r
        loc_x = l + 2 * r
        loc = [loc_x, loc_y, H]
        rot = [P, -90, 0]
        trajectory.append(dict(rotation=rot, location=loc))

    for k in range(math.ceil(n3), math.floor(n4)):
        loc_y = - r - w - r * math.sin(dphi * (k - n3))
        loc_x = l + 2 * r - r * (1 - math.cos(dphi * (k - n3)))
        rot_z = - math.degrees(pi/2 + dphi * (k - n3))
        loc = [loc_x, loc_y, H]
        rot = [P, rot_z, 0]
        trajectory.append(dict(rotation=rot, location=loc))

    for k in range(math.ceil(n4), math.floor(n5)):
        loc_y = - 2 * r - w
        loc_x = l - (k - n4) * s + r
        loc = [loc_x, loc_y, H]
        rot = [P, 180, 0]
        trajectory.append(dict(rotation=rot, location=loc))

    for k in range(math.ceil(n5), math.floor(n6)):
        loc_y = - w - r * (1 + math.cos(dphi * (k - n5)))    # - 2 * r - w + r * math.sin(dphi * (k - n5))
        loc_x = r - r * math.sin(dphi * (k - n5))
        rot_z = - math.degrees(pi + dphi * (k - n5))
        loc = [loc_x, loc_y, H]
        rot = [P, rot_z, 0]
        trajectory.append(dict(rotation=rot, location=loc))

    for k in range(math.ceil(n6), math.floor(n7)):
        loc_y = - r - w + (k - n6) * s
        loc_x = 0
        loc = [loc_x, loc_y, H]
        rot = [P, 90, 0]
        trajectory.append(dict(rotation=rot, location=loc))

    for k in range(math.ceil(n7), math.floor(n)):
        loc_y = - r + r * math.sin(dphi * (k - n7))
        loc_x = r * (1 - math.cos(dphi * (k - n7)))
        loc = [loc_x, loc_y, H]
        rot_z = - math.degrees(1.5 * pi + dphi * (k - n7))
        rot = [P, rot_z, 0]
        trajectory.append(dict(rotation=rot, location=loc))

    return trajectory


def generate_random_traj(s=5):
    """
    Generates semi-random trajectory
    :param s: step length
    :return: numpy array of xy coordinates and respective camera yaw
    """
    xvals, yvals, _ = traj_random.generate_trajectory(variance=200)
    xvals_eq, yvals_eq = traj_random.make_equidistant(xvals, yvals, s)
    ders = traj_random.get_discrete_derivative(xvals_eq, yvals_eq)
    return xvals_eq, yvals_eq, ders


def make_readable(x, y, d):
    """
    Generates the final readable trajectory and corrects pose for UE
    :param x: numpy array of x coordinates
    :param y: numpy array of y coordinates
    :param d: numpy array of yaws
    :return: trajectory as readable list of dicts
    """
    trajectory = []
    for i in range(len(x)):
        rot = [P, -d[i]+90, 0]
        loc = [y[i], x[i], H]
        trajectory.append(dict(rotation=rot, location=loc))
    return trajectory


if __name__ == "__main__":
    import os
    from config import dataset_main_dir
    path = os.path.join(dataset_main_dir, "Trajectory", "metadata.json")
    pitch = str(-P)
    step_distance = str(S)
    info = {
        "map name": map_name,
        "pitch": pitch,
        "step distance": step_distance
    }
    traj = generate_traj(R, S)    # uncomment this for standard path
    # x, y, d = generate_traj2(S)   # uncomment this for random path
    # traj = make_readable(x, y, d) # uncomment this for random path
    metadata = {
        "info": info,
        "trajectory": traj
    }
    save_to_file(path, metadata)
    print("Saved to ", path)
