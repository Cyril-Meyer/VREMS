import skimage.morphology


def get_contours(label):
    return label - skimage.morphology.binary_erosion(label, skimage.morphology.ball(1))


def print_stack_info(stack):
    print(stack.shape, stack.dtype, stack.min(), stack.max())
