# Print EXIF Information onto Photos

**English** | [简体中文](README.md)

## Introduction

This script can read EXIF information from photos, extract the shooting time and GPS coordinates, and use this data to obtain detailed address information. It then adds this information onto the photos, saving new images with geographic location tags and timestamps.

## Sample Image

![Sample Image](https://github.com/fjd2004711/print-exif-to-photo/blob/main/Sample%20image/Sample_image.png)

## Features

- Read EXIF information from photos
- Reverse geocode addresses from GPS coordinates
- Add timestamps and addresses onto photos
- Support for Chinese address format
- Automatic retry and handling of failed operations

## Environment Requirements

- Python version: 3.7 or higher
- Operating Systems: Windows, macOS, Linux
- Proxy environment may be required for users in China

## Installation Requirements

The following Python modules are required to run this script:

- `PIL`
- `geopy`
- `piexif`
- `datetime`

Use the command `pip install -r requirements.txt` to install these libraries.

## How to Use

**This is the `command line` version of the project. We have built an `EXE` executable file for you to use directly, or you can switch to the [GUI branch](https://github.com/fjd2004711/print-exif-to-photo/tree/GUI) to build the project.**

1. Ensure all images are placed in the `images` folder.
2. Run the script:
    ```
   python main.py
   ```
    It will automatically create a folder named `tagged_images` and save new images with timestamps and addresses inside.
3. If processing fails, the script will automatically retry.

### Changing Fonts and Styles

- Add font files to the `fonts` folder.
- Update the `font_path` in `config/style.json` to the desired font path (e.g., `fonts/example.ttf`; the default is `msyh.ttc` for Microsoft YaHei).

#### Configuration File Description

- `font_path`: The path to the font file being used.
- `margin_scale`: The margin ratio, defined as a portion of the image width.
- `font_size_scale_landscape`: The font size scaling factor for landscape images.
- `font_size_scale_portrait`: The font size scaling factor for portrait images.
- `min_font_size`: The minimum font size for text.
- `shadow_color`: The color of the text shadow.
- `shadow_offset`: The offset for the text shadow, in pixels.
- `text_color`: The color of the text.
- `spacing`: The line spacing or the vertical distance between lines.

### Detailed Usage Tutorial

For a detailed usage tutorial, visit [blog.renetxi.com](https://blog.renetxi.com/archives/866).

## Troubleshooting

If you encounter any issues such as EXIF information not being read or address resolution errors, check whether your image files are corrupted and your network connection is functioning properly.

## Contributions

For suggestions for improvements or feature requests, please create an issue or submit a pull request.

## License

This project is licensed under the GPL-3.0 license. For more details, see the `LICENSE` file.  

