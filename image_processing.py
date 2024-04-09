from PIL import Image, ImageDraw, ImageFont, ExifTags
import piexif
import json
from utils import format_time

# 根据图片的EXIF数据调整图片方向
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

# 将度分秒坐标转换为十进制坐标
def dms_to_dd(dms, ref):
    # 计算度、分、秒的十进制值
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0
    # 根据方向调整正负值
    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds
    return degrees + minutes + seconds

def get_exif_data(img_path):
    time_stamp = "未知"
    lat = None
    lon = None

    with open(img_path, 'rb') as img_file:
        exif_dict = piexif.load(img_file.read())

    if 'Exif' in exif_dict and piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
        try:
            time_stamp = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8', 'ignore')
        except UnicodeDecodeError:
            time_stamp = "未知"

    if 'GPS' in exif_dict:
        gps_info = exif_dict['GPS']
        gps_latitude_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef)
        gps_latitude = gps_info.get(piexif.GPSIFD.GPSLatitude)
        gps_longitude_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef)
        gps_longitude = gps_info.get(piexif.GPSIFD.GPSLongitude)

        if gps_latitude_ref and gps_latitude:
            gps_latitude_ref = gps_latitude_ref.decode('utf-8', 'ignore')
            lat = dms_to_dd(gps_latitude, gps_latitude_ref)

        if gps_longitude_ref and gps_longitude:
            gps_longitude_ref = gps_longitude_ref.decode('utf-8', 'ignore')
            lon = dms_to_dd(gps_longitude, gps_longitude_ref)

    return time_stamp, lat, lon

# 重新排序地址信息
def reorder_address(address):
    address_parts = [part.strip() for part in address.split(',')]

    autonomous_region = ''
    province_or_city = ''
    city = ''
    county = ''
    district = ''
    street = ''
    specific = ''

    for part in address_parts:
        if '自治区' in part and not autonomous_region:
            autonomous_region = part
        elif '省' in part and not province_or_city:
            province_or_city = part
        elif '市' in part:
            if part.endswith('市') and not city:
                city = part
        elif '县' in part and not county:
            county = part
        elif '区' in part and not district:
            district = part
        elif any(sub in part for sub in ['街道', '乡', '镇']) and not street:
            street = part
        elif any(sub in part for sub in ['路', '街', '巷']):
            specific = specific + ', ' + part if specific else part
        else:
            specific = specific + ', ' + part if specific else part

    # 过滤空值并拼接地址
    reordered_parts = filter(None, [autonomous_region, province_or_city, city, county, district, street, specific])
    sorted_address = ', '.join(reordered_parts)
    return sorted_address


# 加载配置文件
def load_config(config_path):
    # 打开配置文件并加载JSON内容
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)

# 在图片上添加文本
import json
from PIL import Image, ImageDraw, ImageFont
from utils import format_time

# 加载配置文件的函数
def load_style_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)

# 在图片上添加文本的函数
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
