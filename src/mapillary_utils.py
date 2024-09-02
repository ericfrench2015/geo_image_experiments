import requests
from PIL import Image
from io import BytesIO
import uuid


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