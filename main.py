import os
from PIL import Image, ImageDraw, ImageFont
import piexif

def get_exif_data(img):
    exif_dict = piexif.load(img.info['exif'])
    # 获取时间
    time = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
    # 获取GPS信息
    gps_info = exif_dict['GPS']
    gps_latitude_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef).decode('utf-8')
    gps_latitude = gps_info.get(piexif.GPSIFD.GPSLatitude)
    gps_longitude_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef).decode('utf-8')
    gps_longitude = gps_info.get(piexif.GPSIFD.GPSLongitude)
    return time, (gps_latitude_ref, gps_latitude, gps_longitude_ref, gps_longitude)

def add_text_to_image(img, text, pos):
    draw = ImageDraw.Draw(img)
    font_size = 36
    try:
        font = ImageFont.truetype('arial.ttf', font_size)
    except IOError:
        font = ImageFont.load_default()

    draw.text(pos, text, font=font, fill=(255,255,255))

# 设置图片文件夹路径
folder_path = 'images'  # 替换为你的图片文件夹路径

for filename in os.listdir(folder_path):
    if filename.lower().endswith('.jpg'):
        img_path = os.path.join(folder_path, filename)
        img = Image.open(img_path)

        try:
            time, gps_data = get_exif_data(img)
            gps_info = "Lat: {} Lon: {}".format(gps_data[0:2], gps_data[2:4])

            # 这里仅为示例，您可能需要根据实际的GPS数据格式进行转换

            # 计算文本位置
            width, height = img.size
            text = "{} {}".format(time, gps_info)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype('arial.ttf', 36)

            # 计算文本大小
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 设置文本位置（右下角，10个像素的边距）
            x = width - text_width - 10
            y = height - text_height - 10

            # 添加文本到图片
            add_text_to_image(img, text, (x, y))

            # 保存图片
            img.save(os.path.join(folder_path, 'with_text_'+filename))
        except KeyError:
            print(f"No EXIF data found for {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")