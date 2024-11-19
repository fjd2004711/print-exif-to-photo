import os
import shutil

def create_directories(tagged_folder_path, no_exif_folder_path, failed_folder_path):
    os.makedirs(tagged_folder_path, exist_ok=True)
    os.makedirs(no_exif_folder_path, exist_ok=True)
    os.makedirs(failed_folder_path, exist_ok=True)

def copy_file(src, dst):
    shutil.copy(src, dst)