import numpy as np
import random
from scipy.special import comb
from config import L, W, WIDTH


# mid path lengths
l = L - 0.05*WIDTH
w = W - 0.15*WIDTH


def bernstein_poly(i, n, t):
    """
     The Bernstein polynomial of n, i as a function of t
    """

    return comb(n, i) * (t**(n-i)) * (1 - t)**i


def bezier_curve(points, nTimes=1000):
    """
       Given a set of control points, return the
       bezier curve defined by the control points.

       points should be a list of lists, or list of tuples
       such as [ [1,1],
                 [2,3],
                 [4,5], ..[Xn, Yn] ]
        nTimes is the number of time steps, defaults to 1000

        See http://processingjs.nihongoresources.com/bezierinfo/
    """

    nPoints = len(points)
    xPoints = np.array([p[0] for p in points])
    yPoints = np.array([p[1] for p in points])

    t = np.linspace(0.0, 1.0, nTimes)

    polynomial_array = np.array([bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)])

    # Array comes out in reversed order for some reason, so we have to flip
    xvals = np.flipud(np.dot(xPoints, polynomial_array))
    yvals = np.flipud(np.dot(yPoints, polynomial_array))

    return xvals, yvals


def make_equidistant(x, y, N):
    """
    Makes set of ordered xy coordinates equidistant
    N is desired point distance along curve
    """
    xvals = np.expand_dims(x[0], axis=0)
    yvals = np.expand_dims(y[0], axis=0)
    eucdist = 0.0
    for i in range(1, len(x)):
        eucdist += np.sqrt((x[i] - x[i-1])**2 + (y[i] - y[i-1])**2)
        if eucdist >= N:
            xvals = np.append(xvals, x[i])
            yvals = np.append(yvals, y[i])
            eucdist = 0
    return xvals, yvals


def generate_trajectory(a=90, variance=190, corner_sharpness=3, smoothness=3, nbezier=100000):
    """
    Generates two numpy arrays containing x and y coordinates; points are not equidistant
    a: higher means turns are further away from corners
    variance: in cm; shouldn't be greater than half of path WIDTH
    corner_sharpness: higher is sharper (smaller turning radius)
    smoothness: low is smoother
    nbezier: point density of generated bezier curve
    """
    xpoints = []
    ypoints = []

    # right
    xpoints = np.append(xpoints, [random.triangular(-1, 1, 0) * (variance / 2)])
    ypoints = np.append(ypoints, [random.triangular(-1, 1, -15) * (variance / 2)])
    points = random.randint(2, 4)
    step = l / points
    for i in range(1, points + 1):
        xpoints = np.append(xpoints, [0 + random.triangular(-1, 1, 0) * variance] * smoothness)
        ypoints = np.append(ypoints, [step * i] * smoothness)
    xpoints = np.append(xpoints, [0 + a] * corner_sharpness)
    ypoints = np.append(ypoints, [l + a] * corner_sharpness)
    # top
    points = random.randint(2, 3)
    step = w / points
    for i in range(1, points + 1):
        xpoints = np.append(xpoints, [- step * i] * smoothness)
        ypoints = np.append(ypoints, [l + random.triangular(-1, 1, 0) * variance] * smoothness)
    xpoints = np.append(xpoints, [-w - 1.5*a] * (corner_sharpness + 1))
    ypoints = np.append(ypoints, [l + 1.5*a] * (corner_sharpness + 1))
    # left
    points = random.randint(2, 4)
    step = l / points
    for i in range(1, points + 1):
        xpoints = np.append(xpoints, [- w + random.triangular(-1, 1, 0) * variance] * smoothness)
        ypoints = np.append(ypoints, [l - step * i] * smoothness)
    xpoints = np.append(xpoints, [-w - a] * (corner_sharpness + 2))
    ypoints = np.append(ypoints, [0 - a] * (corner_sharpness + 2))
    # bottom
    points = random.randint(2, 3)
    step = w / points
    for i in range(1, points + 1):
        xpoints = np.append(xpoints, [-w + step * i] * smoothness)
        ypoints = np.append(ypoints, [0 + random.triangular(-1, 1, 0) * variance] * smoothness)
    xpoints = np.append(xpoints, [-WIDTH / 4] * corner_sharpness)
    ypoints = np.append(ypoints, [0] * corner_sharpness)

    points = list(zip(xpoints, ypoints))
    xvals, yvals = bezier_curve(points, nTimes=nbezier)

    return xvals, yvals, points


def get_discrete_derivative(x, y):
    """
    :param x: numpy array of x values
    :param y: numpy array of y values
    :return: numpy array of derivative at each coordinate
    """
    r = len(x)

    der = [np.degrees(np.arctan2((y[1]-y[0]), x[1]-x[0]))]
    for i in range(1, r - 1):
        d = 0.5 * np.degrees(np.arctan2((y[i] - y[i - 1]), (x[i] - x[i - 1]))
                             + np.arctan2((y[i + 1] - y[i]), (x[i + 1] - x[i])))

        der = np.append(der, [d])
    der = np.append(der, [np.degrees(np.arctan2((y[r - 1] - y[r - 2]), (x[r - 1] - x[r - 2])))])
    # for some reason there are always one or two frames that are +180 deg; this just is a quick fix
    for i in range(1, len(der)-1):
        if 270 > np.abs((der[i]-der[i+1])) % 360 > 90:  # if rotation from one frame to the next is greater than 90 deg
            der[i+1] = der[i+1] + 180
            i = i + 1
            print("flipped a frame")

    return der


if __name__ == "__main__":
    from matplotlib import pyplot as plt
    from matplotlib.patches import Rectangle

    xvals, yvals, _ = generate_trajectory()

    xvals_new, yvals_new = make_equidistant(xvals, yvals, N=5)

    fig, ax = plt.subplots()
    # ax.plot(xp, yp, "ro")
    ax.add_patch(Rectangle((-w - WIDTH/2, -WIDTH/2), w + WIDTH, l + WIDTH, color='grey', ec='black'))
    ax.add_patch(Rectangle((-w+WIDTH/2, WIDTH/2), w-WIDTH, l-WIDTH, color='white', ec='black'))

    plt.plot(xvals_new, yvals_new)
    plt.xlim(-1600, 200)
    plt.ylim(-200, 3000)
    ratio = 1.0
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(abs((x_right - x_left) / (y_low - y_high)) * ratio)

    plt.show()
