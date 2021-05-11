from utils import normalize, read_npy
from config import dataset_main_dir, rgb_file_extension
from shutil import copy
from unrealcv import client
import os
import time
from skimage.io import imsave
from PIL import Image
import json

file_path = os.path.join(dataset_main_dir, 'Set_')
traj_file_path = os.path.join(dataset_main_dir, "Trajectory", "metadata.json")

i = 0
k = str(i)
while os.path.exists(file_path + f'{k}'):
    print(file_path + f'{k}')
    i = i+1
    k = str(i)
print(f"Creating Set_{k}")
file_path = file_path + f'{k}'
os.makedirs(file_path + '\\depth')

metadata = json.load(open(traj_file_path))
camera_trajectory = metadata["trajectory"]
client.connect()
if not client.isconnected():
    raise Exception('Client not connected')

# Get object information and divide objects into lists or coloring
print("Assigning colors...")
scene_objects = client.request('vget /objects').split(' ')
floor_objects = [i for i in scene_objects if ('Floor' in i) or ('Path' in i)]
line_objects = [i for i in scene_objects if 'Line' in i]
for obj_id in scene_objects:
    client.request('vset /object/%s/color %s' % (obj_id, '169 0 0'))
for obj_id in floor_objects:
    client.request('vset /object/%s/color %s' % (obj_id, '0 0 0'))
for obj_id in line_objects:
    client.request('vset /object/%s/color %s' % (obj_id, '0 0 0'))
print("Colors assigned...")

overall = 0.0
n_pics = len(camera_trajectory)
copy(traj_file_path, file_path)

for i, coord in enumerate(camera_trajectory):
    start = time.time()

    rot = coord['rotation']
    loc = coord['location']
    client.request('vset /camera/1/location %f %f %f' % (loc[0], loc[1], loc[2]))
    client.request('vset /camera/1/rotation %f %f %f' % (rot[0], rot[1], rot[2]))
    # This is a stupid hack to get the LODs to load, because UE sucks...
    client.request('vset /camera/0/location %f %f %f' % (loc[0], loc[1], loc[2] - 190))

    k = str(i)

    client.request('vget /camera/1/lit %s\\image\\%s.png' % (file_path, k))
    if rgb_file_extension == 'jpg':
        img = Image.open('%s\\image\\%s.png' % (file_path, k)).convert('RGB')
        img.save('%s\\image\\%s.jpg' % (file_path, k), 'jpeg')
        os.remove('%s\\image\\%s.png' % (file_path, k))

    client.request('vget /camera/1/object_mask %s\\object_mask\\%s.png' % (file_path, k))
    img, _, _ = Image.open('%s\\object_mask\\%s.png' % (file_path, k)).convert('RGB').split()
    img.save('%s\\object_mask\\%s.png' % (file_path, k))

    frame_depth = client.request('vget /camera/1/depth npy')
    frame_depth = read_npy(frame_depth)
    frame_depth = normalize(frame_depth)
    imsave(file_path + f'\\depth\\{k}.png', frame_depth)

    # This is just to let the user know how long it will take
    duration = time.time() - start
    overall += duration
    average = overall / (i+1)
    remaining_s = (n_pics - (i+1)) * average
    remaining_min = remaining_s / 60
    display = f'{round(remaining_min, 2)} minutes'
    if remaining_s <= 60:
        display = f'{round(remaining_s)} seconds'
    print(f'{i} of {n_pics} complete\nRemaining time: {display}')

client.disconnect()
