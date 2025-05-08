import os
import sys
import shutil
import time
from PIL import Image
from lib.geolocation import geolocator, is_nominatim_online, reverse_geocode
from lib.utils import generate_user_agent
from lib.exif_utils import get_exif_data
from lib.image_utils import rotate_image_based_on_exif, add_text_to_image
from lib.address_utils import reorder_address

class NoExifException(Exception):
    pass

def process_image(img_path, amap_api_key, nominatim_api, font_size, print_position, user_folders, font_family='msyh.ttc', text_color='#ffffff', shadow_color='#000000', shadow_offset=2, spacing=30):
    """
    处理图片并保存到用户特定的文件夹
    :param img_path: 原始图片路径
    :param amap_api_key: 高德地图API密钥
    :param nominatim_api: 是否使用Nominatim API
    :param font_size: 字体大小
    :param print_position: 水印位置
    :param user_folders: 用户特定的文件夹路径字典
    :param font_family: 字体文件名
    :param text_color: 字体颜色
    :param shadow_color: 阴影颜色
    :param shadow_offset: 阴影粗细
    :param spacing: 行间距
    :return: None
    """
    try:
        img_start_time = time.time()  # 开始处理的时间
        time_stamp, lat, lon, exposure, iso, fnumber, make, model, lens = get_exif_data(img_path)
        if not (lat and lon):
            print(f"没有EXIF信息：{os.path.basename(img_path)}")
            no_exif_img_path = os.path.join(user_folders['no_exif'], f'no_exif_{os.path.basename(img_path)}')
            shutil.copy(img_path, no_exif_img_path)
            raise NoExifException("没有EXIF信息")
        try:
            location = reverse_geocode(geolocator, lat, lon)
            if location:
                reordered_address = reorder_address(location.address)
                img = Image.open(img_path)
                img = rotate_image_based_on_exif(img)
                # 拼接水印内容
                info_lines = [
                    time_stamp,
                    reordered_address,
                    f"{make} {model} {lens}".strip(),
                    f"曝光:{exposure}  光圈:{fnumber}  ISO:{iso}".strip()
                ]
                info_text = '\n'.join([line for line in info_lines if line and line != '未知'])
                img_with_text = add_text_to_image(
                    img, info_text, '', font_size, print_position,
                    font_family=font_family, text_color=text_color, shadow_color=shadow_color,
                    shadow_offset=shadow_offset, spacing=spacing
                )
                # 保存到用户特定的tagged文件夹
                output_path = os.path.join(user_folders['tagged'], os.path.basename(img_path))
                img_with_text.save(output_path)
                print(f"处理成功：文件 '{os.path.basename(img_path)}'")
            else:
                raise ValueError("无法获取地理位置信息")
        except Exception as e:
            if 'HTTPSConnectionPool' in str(e):
                print(f"更换user_agent后重试: {os.path.basename(img_path)}")
                geolocator.headers['User-Agent'] = generate_user_agent()
                location = reverse_geocode(geolocator, lat, lon)
                if location:
                    reordered_address = reorder_address(location.address)
                    img = Image.open(img_path)
                    img = rotate_image_based_on_exif(img)
                    info_lines = [
                        time_stamp,
                        reordered_address,
                        f"{make} {model} {lens}".strip(),
                        f"曝光:{exposure}  光圈:{fnumber}  ISO:{iso}".strip()
                    ]
                    info_text = '\n'.join([line for line in info_lines if line and line != '未知'])
                    img_with_text = add_text_to_image(
                        img, info_text, '', font_size, print_position,
                        font_family=font_family, text_color=text_color, shadow_color=shadow_color,
                        shadow_offset=shadow_offset, spacing=spacing
                    )
                    # 保存到用户特定的tagged文件夹
                    output_path = os.path.join(user_folders['tagged'], os.path.basename(img_path))
                    img_with_text.save(output_path)
                    print(f"重试成功：文件 '{os.path.basename(img_path)}'")
                else:
                    raise ValueError("重试后依然无法获取地理位置信息")
            else:
                raise
        img_end_time = time.time()
        print(f"文件 '{os.path.basename(img_path)}' 处理耗时 {img_end_time - img_start_time:.2f}秒")
    except Exception as e:
        print(f"处理文件 '{os.path.basename(img_path)}' 时发生错误 - {e}")
        # 复制到用户特定的failed文件夹
        failed_img_path = os.path.join(user_folders['failed'], f'failed_{os.path.basename(img_path)}')
        shutil.copy(img_path, failed_img_path)