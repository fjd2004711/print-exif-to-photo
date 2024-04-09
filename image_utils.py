from PIL import Image, ImageDraw, ImageFont, ExifTags
import json
from utils import format_time

def load_style_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)

def rotate_image_based_on_exif(img):
    try:
        # 获取旋转方向的EXIF标签
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(img._getexif().items())

        # 根据旋转方向旋转图片
        if exif[orientation] == 3:
            img = img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img = img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # 如果没有找到EXIF方向信息则忽略
        pass
    return img


def add_text_to_image(img, time_text, address, config_path='style.json'):
    # 加载样式配置
    config = load_style_config(config_path)

    # 判断图片是横向还是纵向，并选择相应的字体大小缩放因子
    if img.width > img.height:
        font_size_scale = config['font_size_scale_landscape']
    else:
        font_size_scale = config['font_size_scale_portrait']

    # 创建绘图对象
    draw = ImageDraw.Draw(img)
    # 根据图片宽度和配置设定的边距比例计算边距
    margin = int(img.width * config['margin_scale'])
    # 使用选定的缩放因子计算字体大小
    font_size = int((img.width / 1920) * font_size_scale)
    # 确保字体大小不小于配置中设定的最小值
    font_size = max(font_size, config['min_font_size'])
    # 加载字体文件
    font = ImageFont.truetype(config['font_path'], font_size)

    # 格式化时间和地址
    time_formatted = format_time(time_text)
    address_formatted = address.rstrip(', 中国')
    text = f"{time_formatted}\n{address_formatted}"

    # 分割文本为多行
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

    # 计算文本的起始y坐标，以便文本在图片底部
    text_y = img.height - margin - text_height

    # 从配置中获取阴影颜色和偏移量
    shadow_color = config['shadow_color']
    shadow_offset = config['shadow_offset']
    # 获取文本颜色
    text_color = config['text_color']

    # 绘制带阴影的文本
    for i, line in enumerate(lines):
        line_width = text_widths[i]
        line_height = line_heights[i] + config['spacing']
        text_x = img.width - margin - line_width
        # 先绘制阴影
        draw.text((text_x + shadow_offset, text_y + shadow_offset), line, font=font, fill=shadow_color)
        # 再绘制文本
        draw.text((text_x, text_y), line, font=font, fill=text_color)
        text_y += line_height

    return img
