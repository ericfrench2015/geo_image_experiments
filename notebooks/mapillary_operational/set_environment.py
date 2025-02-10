import yaml
with open('configuration.yml', 'r') as f:
    config_data = yaml.load(f, Loader=yaml.SafeLoader)

## project-level configurations
sys_path_append = config_data['sys']['sys_path_append']
base_dir = config_data['directory_structure']['base_dir']
image_folder = f"{base_dir}//{config_data['directory_structure']['image_folder']}"
image_metadata_folder = f"{base_dir}//{config_data['directory_structure']['image_metadata_folder']}"
sqlite3_dbname = f"{base_dir}//{config_data['metadata_storage']['sqlite3_dbname']}"
output_folder = f"{base_dir}//{config_data['directory_structure']['output_folder']}"

import os
import sys
sys.path.append(sys_path_append)

import basic_utils as bu

for f in [base_dir, image_folder, image_metadata_folder, output_folder]:
    print(bu.create_folder(f))
