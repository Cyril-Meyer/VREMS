import os
import sys

import numpy as np

import utils
import renderer

# read data
image = np.load("private-data/example_image.npy")
label_1 = np.load("private-data/example_label_1.npy")
label_2 = np.load("private-data/example_label_2.npy")
label_3 = np.load("private-data/example_label_3.npy")

utils.print_stack_info(image)
utils.print_stack_info(label_1)
utils.print_stack_info(label_2)
utils.print_stack_info(label_3)

labels = [utils.get_contours(label_1), utils.get_contours(label_2), utils.get_contours(label_3)]
labels_colors = [[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 0.0, 0.4], [0.0, 0.0, 1.0, 1.0]]

renderer.render_segmentation(image, labels, labels_colors)
