# Print EXIF Information to Photos

**English** | [简体中文](README.md)

## Introduction

This script reads EXIF information from images, extracts the shooting time and GPS coordinates, and uses this data to obtain detailed address information. It then adds this information to the image and saves a new image with geolocation tags and timestamps.

## Example Image

![1](https://github.com/fjd2004711/print-exif-to-photo/blob/main/Sample%20image/Sample_image.png)

## Features

- Read EXIF information from images
- Reverse geocode addresses from GPS coordinates
- Add timestamps and addresses to images
- Support for Chinese address format
- Automatic retry and error handling

## Requirements

- Python version: 3.7 or higher
- Operating System: Windows, macOS, Linux
- Proxy environment required for users in China

## Installation

To run this script, you need to install the following Python modules:

- `PIL`
- `geopy`
- `piexif`
- `datetime`

Please use `pip install -r requirements.txt` to install the required libraries.

## Usage
 **This branch is the `GUI` version of the project, and we have built an `EXE` executable file for you to use directly.**
1. Select the folder containing the images to be processed.
2. Select the output folder for the images.
3. Select the font file (optional).
4. Click the `Start` button and wait for the processing to complete.
5. After processing is complete, return to the selected folder to view the processed images.

### Changing Fonts and Styles

- Place the font file in the `fonts` folder.
- Modify the `font_path` in `config/style.json` to the path of the font. (e.g., `fonts/example.ttf`, default is `msyh.ttc` [Microsoft YaHei])

#### Configuration File Explanation

- `font_path`: Path to the font file used.
- `margin_scale`: Margin scale, defined as a portion of the image width.
- `font_size_scale_landscape`: Font size scale factor for landscape images.
- `font_size_scale_portrait`: Font size scale factor for portrait images.
- `min_font_size`: Minimum font size for the text.
- `shadow_color`: Color of the text shadow.
- `shadow_offset`: Offset of the text shadow (in pixels).
- `text_color`: Color of the text.
- `spacing`: Line spacing, i.e., the vertical distance between lines.

### Detailed Usage Tutorial

[blog.renetxi.com](https://blog.renetxi.com/archives/866)

## Troubleshooting

If you encounter any issues during image processing, such as EXIF information reading failure or address parsing errors, please check if your image files are corrupted and if your network connection is normal.

## Contribution

If you have any suggestions for improvements or feature requests, please create an issue or submit a pull request.

## License

This project is licensed under the GPL-3.0 License. For more details, please see the `LICENSE` file.