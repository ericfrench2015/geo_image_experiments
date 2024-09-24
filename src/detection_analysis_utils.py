from PIL import Image


from matplotlib.path import Path

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon
import matplotlib.path as mplPath
import re


def filter_detections(detection_label, stop_list=[]):
    """
    indicate which detections should be filtered out

    Parameters:
    -detection_label: mapillary detection label
    -stop_list: list of detection fragments from the beginning. Code will
        do a pattern match from beginning of string

    Returns:
    - True: to indicate detection should be filtered
    - False: to indicate the detection should be kept
    """

    if len(stop_list) == 0:
        stop_detection_list = ['regulatory','marking','warning','complementary','object--traffic-sign','information']
    else:
        stop_detection_list = stop_list

    for stop_detection in stop_detection_list:
        if re.match(stop_detection,detection_label):
            return True

    return False
def draw_polygons(polygons, max_x=2200, max_y=1200, display='fill', image_underlay=None, color='green', title=None):
    """
    Draws polygons on top of a background image.

    Parameters:
    - polygons: List of polygons to draw (list of (x, y) coordinates).
    - image_path: Path to the background image.
    - max_x: Maximum x-axis size.
    - max_y: Maximum y-axis size.
    - display: 'fill' or 'outline' to specify whether to fill or outline polygons.
    - image_underlay: pass in the image if you want to see the results on top of the image.
    - color: Color for the polygon.
    - title: passing in the file name is often helpful.

    Returns:
    - normalized_polygon: Normalized polygons (currently not used).
    """

    polygons_for_chart = []

    for polygon in polygons:
        w = []
        y = []
        for xy in polygon:
            w.append(xy[0])
            y.append(xy[1])
        polygons_for_chart.append([w, y])

    # set x figsize, then proportionately set y
    fig_x = 8
    fig_y = int(max_y / (max_x / fig_x))
    fig, ax = plt.subplots(figsize=(fig_x, fig_y))

    if image_underlay is not None:
        ax.imshow(image_underlay, extent=[0, max_x, 0, max_y], aspect='auto')

    for shape in polygons_for_chart:
        if display == 'outline':
            ax.plot(shape[0], shape[1], marker='', markersize=1, color=color)
        elif display == 'fill':
            ax.fill(shape[0], shape[1], color=color)
        else:
            ax.fill(shape[0], shape[1], color=color)

    ax.set_xlim(0, max_x)
    ax.set_ylim(0, max_y)

    # Force the two axes to intersect at 0
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')

    # Adding title and labels
    plt.title(title)
    # plt.xlabel('w')
    # plt.ylabel('y')

    # prevent Jupyter from auto displaying
    plt.close(fig)

    return fig


def detect_relative_pixel_count(coords, step_down=0.01):
    """
    This function counts the relative number of pixels within a polygon.
    On a typical image, this process will take a long time (8-10 seconds)
    To make it prcoess faster, the step_down parameter lets you shrink the
    polygon down for faster performance. Since this is intended to be a way
    to compare/contrast the percent of an image that a particular detection
    takes up, the lost of precision in favor of speed is acceptable.

    :param coords: list of 2-dimensional x/y coordinates
    :param step_down: prct that you want to stp down the polygons


    :return: relative pixel count
    """
    # shrink coords by step_down prct
    small_coords = []
    for c in coords:
        small_coords.append([int(c[0] * step_down), int(c[1] * step_down)])

    polygon = Polygon(small_coords)

    # Step 2: Create a grid of points covering the bounding box of the polygon
    min_x, min_y, max_x, max_y = polygon.bounds

    # min_x = min_x * step_down
    # min_y = min_y * step_down
    # max_x = max_x * step_down
    # max_y = max_y * step_down

    x = np.arange(min_x, max_x + 1)
    y = np.arange(min_y, max_y + 1)
    xx, yy = np.meshgrid(x, y)
    points = np.c_[xx.ravel(), yy.ravel()]

    # Step 3: Check which points lie within the polygon
    path = mplPath.Path(small_coords)
    mask = path.contains_points(small_coords)

    # Step 4: Count the number of pixels (points) within the polygon
    num_pixels_within_polygon = np.sum(mask)
    return num_pixels_within_polygon
    # print(f'Number of pixels within the polygon: {num_pixels_within_polygon}')