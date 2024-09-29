## once dfs are established, this does the searching

import pandas as pd
import numpy as np
import re


def select_detections(df_detections, selected_detection):
    """
    Some detections are a little ambiguous as to their meaning. This function
    helps clarify what certain detections means.

    You can pass in a string with as much or little precision as you want.
    If you pass in low precision (eg. "construction") it will match with all
    detections that begin with construction
    """

    def _get_matched_detections(unqiue_detections, selected_detection):
        matched_detections = []
        for detection in unqiue_detections:
            if re.match(selected_detection, detection):
                matched_detections.append(detection)
        matched_detections.sort()
        return matched_detections

    unique_detections = list(set(df_detections.detection_label.tolist()))
    matched_detections = _get_matched_detections(unique_detections, selected_detection)

    return matched_detections

#selected_detections = select_detections(df_detections, 'construction--fl')

def find_images_matching(df_detections, selected_detections, threshold=5, match_strat='threshold'):
    """
    For each image, if it matches all the passed in detections, return a true

    match_strat is either "all" or "threshold"
    if "all" then only images that match all the detetections will be returned
    if "threshold" then as long as the collective threshold is met, whether it be
    one of 10 detections, the image will be returned

    In ALL cases, images that don't meet the threshold will be ignored

    """

    print(f"original detections count is {len(df_detections)}")

    # first, reduce df to only selected detections
    temp_df = df_detections[df_detections['detection_label'].isin(selected_detections)]
    print(f"after filtering for desired detections: {len(temp_df)}")
    #print(temp_df.shape)

    # for each image, get the detection label count matched and the total percent of image taken
    temp_images = temp_df[['image_id', 'detection_label', 'detection_prct_of_image']].groupby('image_id').agg(
        count_of_detections=('detection_label', 'size'),
        sum_of_detections=('detection_prct_of_image', 'sum')
    ).reset_index()

    # drop images where the aggregate detection prct doesn't meet threshold
    temp_images = temp_images[temp_images.sum_of_detections >= threshold]

    if match_strat == 'threshold':
        matched_images = temp_images.image_id.tolist()
    elif match_strat == 'all':
        matched_images = temp_images.image_id[temp_images.count_of_detections == len(selected_detections)].tolist()
    else:
        print('unexpected match_strat passed... returning threshold')
        matched_images = temp_images.image_id.tolist()

    return matched_images

#matched_images = find_images_matching(df_detections, selected_detections, threshold=10, match_strat='threshold')