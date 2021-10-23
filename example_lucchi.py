import os
import sys

import numpy as np
import tifffile

import utils
import renderer

# read data
image = (tifffile.imread("VREMS-data/lucchi/image.tif")/255).astype(np.float32)
label = (tifffile.imread("VREMS-data/lucchi/label.tif")/255).astype(np.uint8)

utils.print_stack_info(image)
utils.print_stack_info(label)

labels = [utils.get_contours(label)]
labels_colors = [[1.0, 0.0, 0.0, 1.0]]

renderer.render_segmentation(image, labels, labels_colors)
