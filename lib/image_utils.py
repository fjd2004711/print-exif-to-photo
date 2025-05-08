from PIL import Image, ImageDraw, ImageFont, ExifTags
import json
from .utils import format_time

def load_style_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)

def rotate_image_based_on_exif(img):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(img._getexif().items())

        if exif[orientation] == 3:
            img = img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img = img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass
    return img

def add_text_to_image(img, time_text, address, aperture, iso, shutter_speed, selected_info, config_path='config/style.json'):
    config = load_style_config(config_path)

    if img.width > img.height:
        font_size_scale = config['font_size_scale_landscape']
    else:
        font_size_scale = config['font_size_scale_portrait']

    draw = ImageDraw.Draw(img)
    margin = int(img.width * config['margin_scale'])
    font_size = int((img.width / 1920) * font_size_scale)
    font_size = max(font_size, config['min_font_size'])
    font = ImageFont.truetype(config['font_path'], font_size)

    time_formatted = format_time(time_text)
    address_formatted = address.rstrip(', 中国')
    text_parts = []

    if '时间' in selected_info:
        text_parts.append(time_formatted)
    if '地址' in selected_info:
        text_parts.append(address_formatted)
    if '光圈' in selected_info:
        text_parts.append(f"光圈: {aperture}")
    if 'ISO' in selected_info:
        text_parts.append(f"ISO: {iso}")
    if '快门速度' in selected_info:
        text_parts.append(f"快门速度: {shutter_speed}")

    text = '\n'.join(text_parts)

    lines = text.split('\n')
    text_height = 0
    text_widths = []
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_widths.append(bbox[2] - bbox[0])
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        text_height += line_height

    text_y = img.height - margin - text_height

    shadow_color = config['shadow_color']
    shadow_offset = config['shadow_offset']
    text_color = config['text_color']

    for i, line in enumerate(lines):
        line_width = text_widths[i]
        line_height = line_heights[i] + config['spacing']
        text_x = img.width - margin - line_width
        draw.text((text_x + shadow_offset, text_y + shadow_offset), line, font=font, fill=shadow_color)
        draw.text((text_x, text_y), line, font=font, fill=text_color)
        text_y += line_height

    return img