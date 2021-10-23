import numpy as np
import skimage.morphology


def get_contours(label):
    return label - skimage.morphology.binary_erosion(label, skimage.morphology.ball(1))


def print_stack_info(stack):
    print(stack.shape, stack.dtype, stack.min(), stack.max())


def get_colormap(n_labels, alpha=1.0):
    colors = []
    n = int(np.ceil(np.cbrt(n_labels)))
    for r in range(0, n):
        for g in range(0, n):
            for b in range(0, n):
                colors.append([r / n, g / n, b / n, alpha])
    return colors
