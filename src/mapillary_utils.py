import requests
from PIL import Image
from io import BytesIO
import uuid

import numpy as np
import pandas as pd
import base64
import mapbox_vector_tile

from matplotlib.path import Path


def get_mapillary_image(image_id, api_key, image_size_indicator='thumb_2048_url', image_dir="c:\\temp"):
    def _generate_uuid():
        return uuid.uuid4().hex

    def save_image(image, path):
        image.save(path)
        #print(f"Image saved to {path}")

    headers = {
        'Authorization': f'OAuth {api_key}'
    }

    # url = f'https://graph.mapillary.com/{image_id}?fields=thumb_2048_url,captured_at,geometry,height,width'
    url = f'https://graph.mapillary.com/{image_id}?fields={image_size_indicator},captured_at,geometry,height,width,compass_angle,camera_type,camera_parameters,is_pano'

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Get the image URL and metadata from the response
    data = response.json()
    #print(data)
    image_url = data.get(image_size_indicator)
    image_id = data.get('id')
    captured_at = data.get('captured_at')
    geometry = data.get('geometry')
    print(geometry)
    detections = data.get('detections')
    original_height = data.get('height')
    original_width = data.get('width')
    compass_angle = data.get('compass_angle')
    camera_type = data.get('camera_type')
    is_pano = data.get('is_pano')

    camera_params = data.get("camera_parameters")
    if camera_params is not None:

        camera_focal_len = camera_params[0]
        camera_k1 = camera_params[1]
        camera_k2 = camera_params[2]
    else:
        camera_focal_len = None
        camera_k1 = None
        camera_k2 = None


    if not image_url:
        print(f"Image URL not found in the response: {image_url}")
        return None, None

    # Download the image
    image_response = requests.get(image_url)
    image_response.raise_for_status()
    image = Image.open(BytesIO(image_response.content))

    save_image_path = f'{image_dir}//mapillary_{image_id}_{image_size_indicator}.jpg'
    save_image(image, save_image_path)

    metadata = {
        'guid': _generate_uuid(),
        'image_source': 'mapillary',
        'image_id': image_id,
        'captured_at_unix': captured_at,
        'lat': geometry['coordinates'][1],
        'lon': geometry['coordinates'][0],
        'original_height': original_height,
        'original_width': original_width,
        'height': image.height,
        'width': image.width,
        'camera_type': camera_type,
        'compass_angle': compass_angle,
        'is_pano': is_pano,
        'camera_focal_len': camera_focal_len,
        'camera_k1': camera_k1,
        'camera_k2': camera_k2,
        'image_path_on_disk': save_image_path

    }
    return image, metadata


def get_mapillary_detections(image_id, api_key):
    headers = {
        'Authorization': f'OAuth {api_key}'
    }
    url = f'https://graph.mapillary.com/{image_id}/detections?fields=image,value,geometry'
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data

def extract_detections(detections):
    # this parses the json format for detections returned by mapillary
    payload = []
    for element in detections['data']:
        image_id = element['image']['id']
        detection_label = element['value']
        geometry_base64 = element['geometry']
        detection_id = element['id']
        payload.append([image_id, detection_id, detection_label, geometry_base64])

    df = pd.DataFrame(payload, columns=['image_id','detection_id','detection_label','geometry_base64'])

    return df


def decode_base64_geometry_fromdf(row, normalize=False, image_height=None, image_width=None):
    base64_string = row['geometry_base64']
    detection_id = row['detection_id']
    detection_label = row['detection_label']
    image_id = row['image_id']

    def normalize_detection_geometry(polygon, height, width, extent):
        normalized_polygon = []
        w = []
        y = []
        for xy in polygon:
            # TODO: it's weird that the first element is the width and the second is the height
            # should validate this is correct...
            x_pixel_loc = int((xy[0] / extent) * width)
            y_pixel_loc = int((xy[1] / extent) * height)

            w.append(x_pixel_loc)
            y.append(y_pixel_loc)
            normalized_polygon.append([x_pixel_loc, y_pixel_loc])

        return normalized_polygon

    # turn base64 string into a series of x,y coordinates
    decoded_data = base64.decodebytes(base64_string.encode('utf-8'))
    detection_geometry = mapbox_vector_tile.decode(decoded_data)

    # https://www.mapillary.com/developer/api-documentation/
    # mapillary, this needs to be normalized for the image size to get a pixel-by-pixel map
    # I assume this is because the segmentation is done on one size but there are multiple
    # size options when you download, so I guess this is to scale for the size you're working with.

    extent = detection_geometry['mpy-or']['extent']

    # for any given detection id, there can be 1 or more polygon 'features'
    feature_list = []
    # temp_df = pd.DataFrame(columns=['extent','feature_id','feature_properties','coordinates'])
    for feature in detection_geometry['mpy-or']['features']:
        # print(feature)
        coordinates = feature['geometry']['coordinates']
        feature_id = feature['id']
        feature_properties = feature['properties']

        # each feature can have one or more set of coordinates
        for coord_segment in coordinates:
            # print(coord_segment)

            if normalize == True:
                coord_segment = normalize_detection_geometry(coord_segment, image_height, image_width, extent)

            # temp_df.loc[len(temp_df)] = [extent,feature_id,feature_properties,coord_segment]

            # return a 2d array instead and then explode after the fact
            # makes it easier because the feature doesn't contain the image id
            # which we need to keep data integrity

            feature_list.append(
                [image_id, detection_id, detection_label, feature_id, image_height, image_width, extent, feature_properties, coord_segment])

    # return feature_list
    return np.array(feature_list, dtype=object)


def create_image_mask(image_height, image_width, polygon, value=1):
    #polygon is the coordinates
    mask = np.zeros((image_height, image_width), dtype=np.uint8)

    y, x = np.mgrid[:mask.shape[0], :mask.shape[1]]
    points = np.vstack((x.ravel(), y.ravel())).T
    path = Path(polygon)
    mask[path.contains_points(points).reshape(mask.shape)] = value

    return mask