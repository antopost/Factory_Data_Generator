import numpy as np
import cv2
from glob import glob
from natsort import natsorted
import os
import re
import json
from config import dataset_main_dir


def find_obstacles(depth, segmentation):
    """
    Finds all obstacles within circle
    :param depth: gt depth as numpy array
    :param segmentation: gt segmentation as numpy array
    :return: binary obstacle mask as uint8; 255 is obstacle
    """

    # load depth threshold template

    if depth_template is None:
        raise Exception("Depth template could not be found!")

    depth_mask = depth.copy()

    # make binary
    depth_mask[depth_mask > depth_template] = 0.
    depth_mask[depth_mask != 0] = 1.

    # threshold segmentation - all obstacles = 1
    _, obstacles_mask = cv2.threshold(segmentation, segmentation.min()+0.5, 255, cv2.THRESH_BINARY)
    cv2.imshow('obstmask', obstacles_mask)
    # returns all obstacles within depth_thr
    obstacles_mask_close = obstacles_mask.astype(np.float32)*depth_mask

    return obstacles_mask_close


if __name__ == "__main__":
    depth_template = cv2.imread(os.path.join('Templates', 'depth_template_175_P30_depth.png'), 0)
    OBSTACLE = (255, 122, 1)
    FLOOR = (255, 255, 79)
    sets = ['Set_0']
    all_sets = re.findall(r'Set_\d+', str(glob(os.path.join(dataset_main_dir, '*'))))
    print(all_sets)
    seg_extension = 'png'
    depth_enxtension = 'png'

    # Do all sets available sets at once
    if False:
        sets = all_sets

    if os.path.exists(os.path.join(dataset_main_dir)):

        for set in sets:
            print(f"Checking {set} for stop frames.")

            set_path = os.path.join(dataset_main_dir, set)
            depth_gt_paths = natsorted(glob(os.path.join(set_path, 'depth', '*.' + depth_enxtension)))
            seg_paths = natsorted(glob(os.path.join(set_path, 'object_mask', '*.' + seg_extension)))
            rgb_paths = natsorted(glob(os.path.join(set_path, 'image', '*.' + 'jpg')))

            if False:    # for testing
                depth_gt_paths = depth_gt_paths[::40]
                seg_paths = seg_paths[::40]
                rgb_paths = rgb_paths[::40]

            stop_frames = []

            for gt_path, seg_path, rgb_path in zip(depth_gt_paths, seg_paths, rgb_paths):
                gt = cv2.imread(gt_path, 0)
                seg = cv2.imread(seg_path, 0)
                rgb = cv2.imread(rgb_path, 1)

                obs_close = find_obstacles(gt, seg)

                if (dilation == 255).any():
                    temp = re.findall(r'\d+\.jpg', rgb_path)
                    res = int(temp[0].replace(r'.jpg', ''))
                    stop_frames.append(res)

                # For visualization
                obs_close_morphed = (np.dstack((np.zeros(dilation.shape), np.zeros(dilation.shape), dilation))).astype(
                    np.uint8)
                weighted_d = cv2.add(rgb, obs_close_morphed)
                cv2.imshow("morphed", weighted_d)
                
                cv2.waitKey(0)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            with open(os.path.join(set_path, 'stop frames.json'), 'w') as f:
                json.dump(stop_frames, f, indent=4)
            print(f"Stop frames of {set} have been saved.")

    else:
        raise Exception("Path does not exist")
