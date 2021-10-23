import skimage.morphology


def get_contours(label):
    return skimage.morphology.binary_erosion(label, skimage.morphology.ball(1))
