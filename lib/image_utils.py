import json
import os
from PIL import Image, ImageDraw, ImageFont


def rotate_image_based_on_exif(img):
    try:
        # 获取 EXIF 信息
        exif = img._getexif()
        if exif:
            orientation = exif.get(0x0112)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # 处理没有 EXIF 信息或者信息不完整的情况
        pass
    return img


def load_style_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/style.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print('加载样式配置失败:', e)
        return {}


def calculate_font_size_and_position(img_width, img_height, text_width, text_height, mode='auto', margin_scale=0.05):
    """
    根据图片尺寸和文本尺寸计算字体大小和位置。

    :param img_width: 图片宽度
    :param img_height: 图片高度
    :param text_width: 文本宽度
    :param text_height: 文本高度
    :param mode: 模式 ('auto', 'manual')
    :param margin_scale: 边距比例
    :return: (x, y) 坐标
    """
    margin = int(img_width * margin_scale)

    if mode == 'auto':
        # 自动模式：居中显示
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
    else:
        # 手动模式：默认右下角
        x = img_width - margin - text_width
        y = img_height - text_height - margin

    return x, y


def add_text_to_image(img, time_stamp, address, font_size=0, print_position='auto', font_family=None, text_color=None, shadow_color=None, shadow_offset=None, spacing=None):
    style = load_style_config()
    font_path = font_family or style.get('font_path', 'msyh.ttc')
    font_path = os.path.join('fonts', font_path) if not os.path.isabs(font_path) else font_path
    margin_scale = style.get('margin_scale', 0.05)
    spacing = int(spacing) if spacing is not None else style.get('spacing', 30)
    text_color = text_color or style.get('text_color', 'white')
    shadow_color = shadow_color or style.get('shadow_color', 'black')
    shadow_offset = int(shadow_offset) if shadow_offset is not None else style.get('shadow_offset', 2)

    draw = ImageDraw.Draw(img)
    width, height = img.size

    # 去除时间的秒
    if time_stamp and len(time_stamp.split(':')) == 3:
        time_stamp = ':'.join(time_stamp.split(':')[:2])

    # 自动字体大小算法
    if font_size is None or font_size == 0:
        short_edge = min(width, height)
        font_size = max(int(short_edge * 0.05), 12)  # 根据图片短边的 5% 设置字体大小

    # 加载字体
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"字体加载失败: {font_path}, 使用默认字体", e)
        font = ImageFont.load_default()

    text = f"{time_stamp}\n{address}"
    # 计算文本尺寸
    left, top, right, bottom = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align='right')
    text_width = right - left
    text_height = bottom - top

    # 计算水印位置
    margin = int(width * margin_scale)
    if print_position == 'bottom-right':
        x = width - margin - text_width
        y = height - text_height - margin
    elif print_position == 'top-right':
        x = width - margin - text_width
        y = margin
    elif print_position == 'bottom-left':
        x = margin
        y = height - text_height - margin
    else:  # top-left
        x = margin
        y = margin

    # 文字描边（阴影）
    for dx in range(-shadow_offset, shadow_offset + 1):
        for dy in range(-shadow_offset, shadow_offset + 1):
            if dx != 0 or dy != 0:
                draw.multiline_text((x + dx, y + dy), text, font=font, fill=shadow_color, spacing=spacing, align='right')
    # 正文
    draw.multiline_text((x, y), text, font=font, fill=text_color, spacing=spacing, align='right')
    print(f"水印字体:{font_size}, 分辨率:{width}x{height}, 位置:({x}, {y})")
    return img
