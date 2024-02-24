import os
import sys
import shutil
import time
from PIL import Image
from geolocation import geolocator, is_nominatim_online, reverse_geocode
from image_processing import rotate_image_based_on_exif, get_exif_data, add_text_to_image, reorder_address
from utils import generate_user_agent  # 从 utils.py 导入 generate_user_agent 函数

def main():
    folder_path = 'images'  # 替换为你的图片文件夹路径
    tagged_folder_path = os.path.join(folder_path, 'tagged_images')
    no_exif_folder_path = os.path.join(folder_path, 'no_exif_images')
    failed_folder_path = os.path.join(folder_path, 'failed_images')

    # 创建标记图片的文件夹如果它不存在
    if not os.path.exists(tagged_folder_path):
        os.makedirs(tagged_folder_path)
    if not os.path.exists(no_exif_folder_path):
        os.makedirs(no_exif_folder_path)
    if not os.path.exists(failed_folder_path):
        os.makedirs(failed_folder_path)

    # 初始化失败图片列表
    failed_images = []

    # 检查 Nominatim 服务状态
    check_start_time = time.time()
    if not is_nominatim_online(geolocator):
        print("Nominatim 服务当前不可用。请稍后重试。")
        sys.exit(1)
    check_end_time = time.time()
    print(f"Nominatim 服务状态检查耗时：{check_end_time - check_start_time:.2f}秒。")

    # 开始处理图片
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpg'):
            img_path = os.path.join(folder_path, filename)
            try:
                img_start_time = time.time()  # 开始处理的时间
                time_stamp, lat, lon = get_exif_data(img_path)
                if lat and lon:
                    try:
                        location = reverse_geocode(geolocator, lat, lon)
                        if location:
                            reordered_address = reorder_address(location.address)
                            img = Image.open(img_path)
                            img = rotate_image_based_on_exif(img)
                            img_with_text = add_text_to_image(img, time_stamp, reordered_address)
                            img_with_text.save(os.path.join(tagged_folder_path, filename))
                            print(f"处理成功：文件 '{filename}'")
                        else:
                            raise ValueError("无法获取地理位置信息")
                    except Exception as e:
                        if 'HTTPSConnectionPool' in str(e):
                            print(f"更换user_agent后重试: {filename}")
                            geolocator.headers['User-Agent'] = generate_user_agent()
                            location = reverse_geocode(geolocator, lat, lon)
                            if location:
                                reordered_address = reorder_address(location.address)
                                img = Image.open(img_path)
                                img = rotate_image_based_on_exif(img)
                                img_with_text = add_text_to_image(img, time_stamp, reordered_address)
                                img_with_text.save(os.path.join(tagged_folder_path, filename))
                                print(f"重试成功：文件 '{filename}'")
                            else:
                                raise ValueError("重试后依然无法获取地理位置信息")
                        else:
                            raise
                else:
                    print(f"没有EXIF信息：{filename}")
                    no_exif_img_path = os.path.join(no_exif_folder_path, f'no_exif_{filename}')
                    shutil.copy(img_path, no_exif_img_path)  # 标记没有EXIF信息的图片
                    continue  # 跳过后续的异常处理
                img_end_time = time.time()
                print(f"文件 '{filename}' 处理耗时 {img_end_time - img_start_time:.2f}秒")
            except Exception as e:
                print(f"处理文件 '{filename}' 时发生错误 - {e}")
                failed_images.append(filename)
                failed_img_path = os.path.join(failed_folder_path, f'failed_{filename}')
                shutil.copy(img_path, failed_img_path)  # 复制原始图片到failed_images文件夹并添加前缀

    # 输出失败的图片
    if failed_images:
        print("以下文件处理失败:")
        for failed_image in failed_images:
            print(failed_image)

if __name__ == "__main__":
    main()