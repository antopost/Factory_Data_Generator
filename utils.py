import cv2
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO


def read_png(res):
    """Converts string of bytes to readable image"""
    nparr = np.frombuffer(res, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img_np


def read_npy(res):
    """Converts bytes to readable image"""
    nparr = np.load(BytesIO(res))
    return nparr


def normalize(src, max_depth=1500, min_depth=10):
    """Truncates and normalizes numpy array to display as depth map"""
    src[src > max_depth] = max_depth
    src[src < min_depth] = min_depth
    src = src.astype('float') / max_depth * 255
    src = np.rint(src)
    normalized = np.uint8(src)

    return normalized


def heatmap(src):
    """Turns grayscale depth map into heatmap"""
    colormap = plt.get_cmap('inferno')
    heatmap = (colormap(src) * 2 ** 16).astype(np.uint16)[:, :, :3]
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_RGB2BGR)
    return heatmap