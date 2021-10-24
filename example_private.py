import os
import sys
import logging

import numpy as np
import tifffile

import utils
import renderer

logging.basicConfig(level=logging.DEBUG)

# read data
image = np.load("private-data/example_image.npy")
label_1 = np.load("private-data/example_label_1.npy")
label_2 = np.load("private-data/example_label_2.npy")
label_3 = np.load("private-data/example_label_3.npy")

# image = np.rollaxis(tifffile.imread("private-data/image_crop.tif"), 1)
# label_1 = np.rollaxis(tifffile.imread("private-data/prediction_mito_pp_cls2.tif"), 1)
# label_2 = np.rollaxis(tifffile.imread("private-data/prediction_cell_pp_cls2.tif"), 1)
# label_3 = np.rollaxis(tifffile.imread("private-data/prediction_reti_pp_cls2.tif"), 1)

utils.print_stack_info(image)
labels = [utils.get_contours(label_1),
          utils.get_contours(label_3),
          utils.get_contours(label_2)]

labels_colors = [[1.0, 0.0, 0.0, 1.0],
                 [0.0, 0.0, 1.0, 0.5],
                 [0.0, 1.0, 0.0, 0.25]]

renderer.render_segmentation(image,
                             labels,
                             labels_colors,
                             rotation_speed=0.20)
