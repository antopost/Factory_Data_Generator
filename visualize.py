import numpy as np
import cv2
from glob import glob
from natsort import natsorted
import os
from config import dataset_main_dir

sets = ['Set_20']
seg_template = cv2.imread(os.path.join(dataset_main_dir, 'template_175_P30_mask.png'), 0)
seg_template[seg_template != 0] = 1
circle = cv2.imread(os.path.join(dataset_main_dir, 'circle.png'), 0)
s = circle.shape
circle = (np.dstack((np.zeros(s), np.zeros(s), circle))).astype(np.uint8)
add_circle = True
show_frame = False
show_reference = False
start = 0

for set in sets:
    set_path = os.path.join(dataset_main_dir, set)
    rgb_paths = natsorted(glob(os.path.join(set_path, 'image', '*.jpg')))
    depth_template = cv2.imread(os.path.join(dataset_main_dir, 'template_175_P30_depth.png'), 0)
    depth_paths = natsorted(glob(os.path.join(set_path, 'depth', '*.png')))

    rgb_paths = rgb_paths[start:]
    depth_paths = depth_paths[start:]
    for i, (rgb_path, depth_path) in enumerate(zip(rgb_paths, depth_paths)):

        # Visualization
        rgb = cv2.imread(rgb_path)
        depth = cv2.imread(depth_path, 0)
        depth[depth >= depth_template] = 0
        depth[depth!=0] = 255
        red_mask_is = (np.dstack((np.zeros(s), np.zeros(s), depth))).astype(np.uint8)
        masked = cv2.add(rgb, red_mask_is)
        stop = masked[:,:,2]==255
        if stop.any():
            print("STOP", i+start)
        if add_circle:
            masked = cv2.add(masked, circle)
        if show_frame:
            coords = (580, 470)
            if i+start > 999:
                coords = (561, 470)
            masekd = cv2.putText(masked, str(i+start), coords, cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), thickness=2)
        cv2.imshow("rgb masked", masked)

        key = cv2.waitKey(0)
        if key == ord('q'):
            break
