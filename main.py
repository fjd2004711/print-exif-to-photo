import os
from PIL import Image, ImageDraw, ImageFont
from geopy.geocoders import Nominatim
import piexif

# 创建一个geolocator对象
geolocator = Nominatim(user_agent="geo_tagging_app")


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
    # 在此处初始化变量，以防EXIF数据不存在
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

    # 初始化各个组成部分
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

def add_text_to_image(img_path, text, font_path='msyh.ttc', font_size=48):
    # 加载图片
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)

    # 加载字体文件和指定大小
    font = ImageFont.truetype(font_path, font_size)

    # 分割时间和地址，并移除地址中的“中国”
    time, address = text.split(', 位置: ')
    address = address.replace("中国", "").strip()

    # 使用自定义函数对地址进行排序
    sorted_address = reorder_address(address)
    text = f"{time}\n{address}"  # 组合成新的文本

    # 使用textbbox获取每行文本的边界框，计算总文本大小
    text_lines = text.split('\n')
    max_width = 0
    total_height = 0
    for line in text_lines:
        line_bbox = draw.textbbox((0, 0), line, font=font)
        line_width = line_bbox[2] - line_bbox[0]
        line_height = line_bbox[3] - line_bbox[1]
        max_width = max(max_width, line_width)
        total_height += line_height

    # 设置边距大小
    margin_percentage = 0.05
    x_margin = img.width * margin_percentage
    y_margin = img.height * margin_percentage

    # 文本在图片上的x和y坐标（右下角）
    text_x = img.width - max_width - x_margin
    text_y = img.height - total_height - y_margin - font_size * (len(text_lines) - 1)  # 减去行高

    # 阴影的颜色和变量
    shadow_color = "black"
    shadow_offset = 2

    # 绘制文本阴影和前景
    for line in text_lines:
        # 绘制阴影文本
        shadow_position = (text_x + shadow_offset, text_y + shadow_offset)
        draw.text(shadow_position, line, font=font, fill=shadow_color)
        # 绘制前景文本
        draw.text((text_x, text_y), line, font=font, fill="white")

        # 更新y坐标为下一行的位置
        line_bbox = draw.textbbox((text_x, text_y), line, font=font)
        text_y += line_bbox[3] - line_bbox[1] + font_size  # 加上行高

    return img


# 设置图片文件夹路径
folder_path = 'images'  # 替换为你的图片文件夹路径
tagged_folder_path = os.path.join(folder_path, 'tagged_images')

# 确保目标文件夹存在
if not os.path.exists(tagged_folder_path):
    os.makedirs(tagged_folder_path)

# 遍历图片文件夹中的图片文件
for filename in os.listdir(folder_path):
    if filename.lower().endswith('.jpg'):
        img_path = os.path.join(folder_path, filename)
        try:
            time, lat, lon = get_exif_data(img_path)
            if lat and lon:
                location = geolocator.reverse((lat, lon), language='zh')
                reordered_address = reorder_address(location.address)
                text_to_add = f"拍摄时间: {time}, 位置: {reordered_address}"
                img_with_text = add_text_to_image(img_path, text_to_add)  # 添加文本到图片
                img_with_text.save(os.path.join(tagged_folder_path, filename))  # 保存带标签的图片

                print(
                    f"处理成功：文件 '{filename}' - 拍摄时间：{time}, 原始位置：{location.address}, 重排序后位置：{reordered_address}")
            else:
                print(f"警告：文件 '{filename}' 没有有效的GPS信息。")
        except Exception as e:
            print(f"错误：处理文件 '{filename}' 时出现问题 - {e}")