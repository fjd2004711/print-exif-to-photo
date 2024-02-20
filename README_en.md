# Print EXIF Information onto Images

**English** | [简体中文](README.md)

## Introduction
This script can extract EXIF information from images, including the time the photo was taken and the GPS coordinates, and use this data to retrieve detailed address information. The script will then overlay this information onto the photos and save new images with geographic location tags and timestamps.

## Features
- Read and extract EXIF information from photos
- Reverse geocode address using GPS coordinates
- Overlay timestamps and address information onto images
- Support formatting for Chinese addresses
- Automated retries for failed operations

## Environmental Requirements
- Python Version: 3.7 or higher
- Operating Systems: Compatible with Windows, macOS, Linux

## Installation Requirements
The following Python modules are required to execute this script:
- PIL (Pillow)
- geopy
- piexif
- datetime

Use `pip install -r requirements.txt` to install the required libraries.

## Usage
1. Ensure all images are located in the `images` directory.
2. Execute the script, it will automatically create a directory named `tagged_images` and will save the new images with timestamps and addresses in this directory.
3. In case of any processing failure, 

### Change Font
- Place the font file into the `font` folder.
- Update the `font_path` in the code to the path of the new font.

## Troubleshooting
Should any issues arise during the image processing, such as failure to read EXIF information or errors in address resolution, verify the integrity of your image files and ensure there is a stable network connection.

## Contributing
For any suggestions for improvements or requests for new features, please create an issue or submit a pull request.

## License
This project is under the GPL-3.0 license. Please see the `LICENSE` file for more details.