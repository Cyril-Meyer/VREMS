import os
import sys
import logging

import numpy as np

import utils
import renderer

logging.basicConfig(level=logging.DEBUG)

# read data
image = np.load("VREMS-data/heinrich/image_jrc_hela-2_crop3.npy")
labels = np.load("VREMS-data/heinrich/labels_jrc_hela-2_crop3.npy")

# image = np.load("VREMS-data/heinrich/image_jrc_hela-2_crop113.npy")
# labels = np.load("VREMS-data/heinrich/labels_jrc_hela-2_crop113.npy")

# image = np.load("VREMS-data/heinrich/image_jrc_hela-3_crop111.npy")
# labels = np.load("VREMS-data/heinrich/labels_jrc_hela-3_crop111.npy")

# image = np.load("VREMS-data/heinrich/image_jrc_jurkat-1_crop112.npy")
# labels = np.load("VREMS-data/heinrich/labels_jrc_jurkat-1_crop112.npy")

# image = np.load("VREMS-data/heinrich/image_jrc_macrophage-2_crop110.npy")
# labels = np.load("VREMS-data/heinrich/labels_jrc_macrophage-2_crop110.npy")

labels_array = []
for v in np.unique(labels):
    labels_array.append(utils.get_contours((labels == v)*1))

utils.print_stack_info(image)
utils.print_stack_info(np.array(labels_array))

labels_colors = utils.get_colormap(len(np.unique(labels)), alpha=0.25)

renderer.render_segmentation(image,
                             labels_array,
                             labels_colors,
                             rotation_speed=0.5,
                             view_distance=1.0,
                             # capture=1800,
                             # output="heinrich.mp4",
                             video_fps=60)
