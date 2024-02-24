from PIL import Image, ImageDraw, ImageFont, ExifTags
import piexif
from utils import format_time

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

    reordered_parts = filter(None, [autonomous_region, province_or_city, city, county, district, street, specific])
    sorted_address = ', '.join(reordered_parts)
    return sorted_address

def add_text_to_image(img, time_text, address, font_path='msyh.ttc', spacing=30):
    draw = ImageDraw.Draw(img)
    margin = int(img.width * 0.05)
    font_size = int((img.width / 1920) * 48)
    font_size = max(font_size, 20)
    font = ImageFont.truetype(font_path, font_size)

    time_formatted = format_time(time_text)
    address_formatted = address.rstrip(', 中国')

    text = f"{time_formatted}\n{address_formatted}"

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
    shadow_color = "black"
    shadow_offset = 2

    for i, line in enumerate(lines):
        line_width = text_widths[i]
        line_height = line_heights[i] + spacing
        text_x = img.width - margin - line_width
        draw.text((text_x + shadow_offset, text_y + shadow_offset), line, font=font, fill=shadow_color)
        draw.text((text_x, text_y), line, font=font, fill="white")
        text_y += line_height

    return img