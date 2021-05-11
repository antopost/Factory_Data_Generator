from unrealcv import client
import cv2
import json
from utils import read_png, read_npy, normalize, heatmap
import os
from config import dataset_main_dir


# OBSTACLE_COLOR = '255 122 1'
# FLOOR_COLOR = '255 255 79'
# LINE_COLOR = '128 0 128'

camera_trajectory = json.load(open(os.path.join(dataset_main_dir, 'Trajectory', 'metadata.json')))["trajectory"]
print(len(camera_trajectory))
client.connect()

# Get object information and divide objects into lists or coloring
scene_objects = client.request('vget /objects').split(' ')
floor_objects = [i for i in scene_objects if ('Floor' in i) or ('Path' in i)]
line_objects = [i for i in scene_objects if 'Line' in i]

# print("Assigning colors...")
# for obj_id in scene_objects:
#     client.request('vset /object/%s/color %s' % (obj_id, OBSTACLE_COLOR))
# for obj_id in floor_objects:
#     client.request('vset /object/%s/color %s' % (obj_id, FLOOR_COLOR))
# for obj_id in line_objects:
#     client.request('vset /object/%s/color %s' % (obj_id, LINE_COLOR))
# print("Colors assigned...")

run = True
while client.isconnected() & run:

    # for coord in camera_trajectory:
    for count, coord in enumerate(camera_trajectory[::8]):

        rot = coord['rotation']
        loc = coord['location']

        client.request('vset /camera/1/location %f %f %f' % (loc[0], loc[1], loc[2]))
        client.request('vset /camera/1/rotation %f %f %f' % (rot[0], rot[1], rot[2]))
        # This is a stupid hack to get the LODs to load, because UE sucks...
        client.request('vset /camera/0/location %f %f %f' % (loc[0], loc[1], loc[2]-190))

        frame_lit = client.request('vget /camera/1/lit png')
        frame_lit = read_png(frame_lit)
        print(frame_lit)
        frame_mask = client.request('vget /camera/1/object_mask png')
        frame_mask = read_png(frame_mask)
        frame_depth = client.request('vget /camera/1/depth npy')
        frame_depth = read_npy(frame_depth)
        frame_depth = normalize(frame_depth)
        frame_depth = heatmap(frame_depth)

        cv2.imshow('frame_lit', frame_lit)
        cv2.imshow('frame_mask', frame_mask)
        cv2.imshow('frame_depth', frame_depth)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            run = False
            break

client.disconnect()
cv2.destroyAllWindows()
