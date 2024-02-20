import os
import random
import string
from PIL import Image, ImageDraw, ImageFont
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from datetime import datetime
import piexif

# 创建新的user_agent函数
def generate_user_agent():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

# 初始化 geolocator
geolocator = Nominatim(user_agent=generate_user_agent())

def dms_to_dd(dms, ref):
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0
    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds
    return degrees + minutes + seconds


def get_exif_data(img_path):
    time = "Unknown"
    lat = None
    lon = None

    with open(img_path, 'rb') as img_file:
        exif_dict = piexif.load(img_file.read())

    if 'Exif' in exif_dict and piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
        time = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')

    if 'GPS' in exif_dict:
        gps_info = exif_dict['GPS']
        gps_latitude_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef)
        gps_latitude = gps_info.get(piexif.GPSIFD.GPSLatitude)
        gps_longitude_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef)
        gps_longitude = gps_info.get(piexif.GPSIFD.GPSLongitude)

        if gps_latitude_ref and gps_latitude:
            gps_latitude_ref = gps_latitude_ref.decode('utf-8')
            lat = dms_to_dd(gps_latitude, gps_latitude_ref)

        if gps_longitude_ref and gps_longitude:
            gps_longitude_ref = gps_longitude_ref.decode('utf-8')
            lon = dms_to_dd(gps_longitude, gps_longitude_ref)

    return time, lat, lon


def reorder_address(address):
    address_parts = [part.strip() for part in address.split(',')]

    autonomous_region = ''
    province_or_city = ''
    city = ''
    county = ''
    district = ''
    street = ''
    specific = ''

    # 遍历并识别各部分
    for part in address_parts:
        if '自治区' in part and not autonomous_region:
            autonomous_region = part
        elif ('省' in part or '市' in part) and part.endswith('市'):
            city = part
        elif '市' in part and not province_or_city:
            province_or_city = part
        elif any(sub in part for sub in ['县', '区']) and not county:
            county = part
        elif any(sub in part for sub in ['街道', '乡', '镇']) and not district:
            district = part
        elif any(sub in part for sub in ['路', '街', '巷']) and not street:
            street = part
        else:
            specific += part if not specific else ', ' + part

    # 根据中国的地址习惯进行排列，优先级从高到低
    reordered_parts = filter(None, [autonomous_region, province_or_city, city, county, district, street, specific])
    sorted_address = ', '.join(reordered_parts)
    return sorted_address

def format_time(time_str):
    # 转换时间格式从 "YYYY:MM:DD HH:MM:SS" 到 "YYYY年MM月DD日 HH:MM"
    try:
        original_format = "%Y:%m:%d %H:%M:%S"
        target_format = "%Y年%m月%d日 %H:%M"
        return datetime.strptime(time_str, original_format).strftime(target_format)
    except ValueError:
        return "时间未知"


def add_text_to_image(img_path, time, address, font_path='msyh.ttc', spacing=10):
    # 加载图片
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)

    # 设置边距
    margin = int(img.width * 0.05)  # 例如图片宽度的1%
    font_size = int((img.width / 1920) * 48)  # 调整基准字体大小
    font_size = max(font_size, 20)  # 保证最小字体大小
    font = ImageFont.truetype(font_path, font_size)

    # 格式化时间和地址
    time_formatted = format_time(time)
    address_formatted = address.rstrip(', 中国')

    # 组合文本
    text = f"{time_formatted}\n{address_formatted}"

    # 预计算每行文本的高度
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

    # 文本在图片上的x和y坐标（右下角）
    text_y = img.height - margin - text_height

    # 阴影颜色和偏移
    shadow_color = "black"
    shadow_offset = 2

    # 绘制每行文本
    for i, line in enumerate(lines):
        line_width = text_widths[i]
        line_height = line_heights[i] + spacing  # 增加额外的行间距
        # 计算每行的x坐标以保持右对齐
        text_x = img.width - margin - line_width
        # 绘制阴影部分
        draw.text((text_x + shadow_offset, text_y + shadow_offset), line, font=font, fill=shadow_color)
        # 绘制文本部分
        draw.text((text_x, text_y), line, font=font, fill="white")
        # 下一行y坐标
        text_y += line_height

    return img

# 设置图片文件夹路径
folder_path = 'images'    # 替换为你的图片文件夹路径
tagged_folder_path = os.path.join(folder_path, 'tagged_images')

# 创建标记图片的文件夹如果它不存在
if not os.path.exists(tagged_folder_path):
    os.makedirs(tagged_folder_path)

# 初始化失败图片列表
failed_images = []

for filename in os.listdir(folder_path):
    if filename.lower().endswith('.jpg'):
        img_path = os.path.join(folder_path, filename)
        try:
            time, lat, lon = get_exif_data(img_path)
            if lat and lon:
                try:
                    location = geolocator.reverse((lat, lon), language='zh')
                except GeocoderTimedOut as e:
                    print(f"警告：文件'{filename}'处理失败，原因: 请求超时。")
                    failed_images.append(filename)
                    continue

                reordered_address = reorder_address(location.address)
                img_with_text = add_text_to_image(img_path, time, reordered_address)
                # 设置带有标签的图片的保存路径
                img_with_text.save(os.path.join(tagged_folder_path, filename))
                print(f"处理成功：文件 '{filename}'- 拍摄时间：{time}, 原始位置：{location.address}, 重排序后位置：{reordered_address}")
            else:
                print(f"警告：文件 '{filename}' 没有有效的GPS信息。")
        except Exception as e:
            print(f"错误：处理文件 '{filename}' 时出现问题 - {str(e)}")
            failed_images.append(filename)

# 重试处理失败的图片
if failed_images:
    print("正在重试处理失败的图片...")
    user_agent = generate_user_agent()
    geolocator = Nominatim(user_agent=user_agent)
    print(f"更新user_agent至: '{user_agent}'")

    for filename in failed_images:
        img_path = os.path.join(folder_path, filename)
        try:
            time, lat, lon = get_exif_data(img_path)
            if lat and lon:
                try:
                    location = geolocator.reverse((lat, lon), language='zh')
                except GeocoderTimedOut as e:
                    print(f"重新处理失败：文件'{filename}'，原因: 请求超时。")
                    continue

                reordered_address = reorder_address(location.address)
                img_with_text = add_text_to_image(img_path, time, reordered_address)
                # 设置带有标签的图片的保存路径
                img_with_text.save(os.path.join(tagged_folder_path, filename))
                print(f"重新处理成功：文件 '{filename}'")
            else:
                print(f"警告：文件 '{filename}' 在重新处理中没有有效的GPS信息。")
        except Exception as e:
            print(f"重新处理错误：处理文件 '{filename}' 时出现问题 - {str(e)}")