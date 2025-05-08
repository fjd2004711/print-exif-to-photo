import os
import sys
import shutil
import time
from PIL import Image
from lib.utils import generate_user_agent
from lib.exif_utils import get_exif_data
from lib.image_utils import rotate_image_based_on_exif, add_text_to_image
from lib.address_utils import reorder_address
from lib.geolocation import is_nominatim_online, reverse_geocode
import traceback


def main():
    folder_path = 'images'
    tagged_folder_path = os.path.join(folder_path, 'tagged_images')
    no_exif_folder_path = os.path.join(folder_path, 'no_exif_images')
    failed_folder_path = os.path.join(folder_path, 'failed_images')

    if not os.path.exists(tagged_folder_path):
        os.makedirs(tagged_folder_path)
    if not os.path.exists(no_exif_folder_path):
        os.makedirs(no_exif_folder_path)
    if not os.path.exists(failed_folder_path):
        os.makedirs(failed_folder_path)

    failed_images = []

    check_start_time = time.time()
    if not is_nominatim_online():
        print("Nominatim 服务当前不可用。请稍后重试。")
        sys.exit(1)
    check_end_time = time.time()
    print(f"Nominatim 服务状态检查耗时：{check_end_time - check_start_time:.2f}秒。")

    print("请选择地址解析 API：")
    print("1. 高德地图 API")
    print("2. Nominatim")
    while True:
        api_choice = input("请输入序号 (1 或 2): ")
        if api_choice == '1':
            use_amap = True
            break
        elif api_choice == '2':
            use_amap = False
            break
        else:
            print("输入无效，请输入 1 或 2。")

    available_info = ['时间', '地址', '光圈', 'ISO', '快门速度']
    print("请选择要打印在照片上的信息（输入序号，用逗号分隔，例如：1,2,3）：")
    for i, info in enumerate(available_info, start=1):
        print(f"{i}. {info}")

    while True:
        selection = input().split(',')
        valid_selection = []
        for index in selection:
            try:
                num = int(index)
                if 1 <= num <= len(available_info):
                    valid_selection.append(num)
            except ValueError:
                pass

        if valid_selection:
            selected_info = [available_info[num - 1] for num in valid_selection]
            break
        else:
            print("输入无效，请输入有效的序号，用逗号分隔。")

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpg'):
            img_path = os.path.join(folder_path, filename)
            try:
                img_start_time = time.time()
                time_stamp, lat, lon, aperture, iso, shutter_speed = get_exif_data(img_path)
                if lat and lon:
                    try:
                        location = reverse_geocode(lat, lon, use_amap)
                        if location:
                            reordered_address = reorder_address(location.address)
                            img = Image.open(img_path)
                            img = rotate_image_based_on_exif(img)
                            img_with_text = add_text_to_image(img, time_stamp, reordered_address, aperture, iso, shutter_speed, selected_info)
                            img_with_text.save(os.path.join(tagged_folder_path, filename))
                            print(f"处理成功：文件 '{filename}'")
                        else:
                            raise ValueError("无法获取地理位置信息")
                    except Exception as e:
                        if 'HTTPSConnectionPool' in str(e):
                            print(f"更换user_agent后重试: {filename}")
                            location = reverse_geocode(lat, lon, use_amap)
                            if location:
                                reordered_address = reorder_address(location.address)
                                img = Image.open(img_path)
                                img = rotate_image_based_on_exif(img)
                                img_with_text = add_text_to_image(img, time_stamp, reordered_address, aperture, iso, shutter_speed, selected_info)
                                img_with_text.save(os.path.join(tagged_folder_path, filename))
                                print(f"重试成功：文件 '{filename}'")
                            else:
                                raise ValueError("重试后依然无法获取地理位置信息")
                        else:
                            print(f"处理文件 '{filename}' 时发生错误: {str(e)}")
                            print(traceback.format_exc())
                            failed_images.append(filename)
                            failed_img_path = os.path.join(failed_folder_path, f'failed_{filename}')
                            shutil.copy(img_path, failed_img_path)
                else:
                    print(f"没有EXIF信息：{filename}")
                    no_exif_img_path = os.path.join(no_exif_folder_path, f'no_exif_{filename}')
                    shutil.copy(img_path, no_exif_img_path)
                    continue
                img_end_time = time.time()
                print(f"文件 '{filename}' 处理耗时 {img_end_time - img_start_time:.2f}秒")
            except Exception as e:
                print(f"处理文件 '{filename}' 时发生错误: {str(e)}")
                print(traceback.format_exc())
                failed_images.append(filename)
                failed_img_path = os.path.join(failed_folder_path, f'failed_{filename}')
                shutil.copy(img_path, failed_img_path)

    if failed_images:
        print("以下文件处理失败:")
        for failed_image in failed_images:
            print(failed_image)


if __name__ == "__main__":
    main()
