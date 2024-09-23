from PIL import Image
from io import BytesIO

def get_thumbnail(image, prct=0.4):
    """
    Creates a thumbnail of the given image based on the specified percentage of its original dimensions.

    Parameters:
    - image: A PIL Image object. The image to be resized into a thumbnail.
    - prct: float. A percentage (between 0 and 1) that determines the size of the thumbnail relative to the original image dimensions.

    Returns:
    - small_image: A PIL Image object. The thumbnail version of the original image.

    """

    small_image = image.copy()

    small_w = int(image.size[0] * prct)
    small_h = int(image.size[1] * prct)
    # size = (small_h, small_w)
    small_image.thumbnail((small_h, small_w))


    return small_image