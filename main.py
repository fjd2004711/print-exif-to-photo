import os
import time
import threading
import logging
from tkinter import Tk, Button, Label, Text, Scrollbar, ttk
from PIL import Image, ImageTk
import webbrowser
from lib.geolocation import geolocator, is_nominatim_online, reverse_geocode
from lib.utils import generate_user_agent
from lib.exif_utils import get_exif_data
from lib.image_utils import rotate_image_based_on_exif, add_text_to_image
from lib.address_utils import reorder_address
from lib.file_utils import create_directories, copy_file
from lib.gui_utils import select_folder, show_error, show_info

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 全局变量
input_folder_path = None
output_folder_path = None
current_image_index = 0
total_image_count = 0
failed_images_info = []
processing_images_count = 0
failed_images_count = 0
no_exif_images_count = 0

def log_to_gui(message):
    result_text.insert('end', message + '\n')
    result_text.see('end')

def main(input_folder_path, output_folder_path):
    global current_image_index, total_image_count, processing_images_count, failed_images_count, no_exif_images_count
    tagged_folder_path = os.path.join(output_folder_path, 'tagged_images')
    no_exif_folder_path = os.path.join(output_folder_path, 'no_exif_images')
    failed_folder_path = os.path.join(output_folder_path, 'failed_images')

    # 创建目录
    create_directories(tagged_folder_path, no_exif_folder_path, failed_folder_path)

    # 初始化失败图片列表
    failed_images = []

    # 检查Nominatim服务状态
    check_start_time = time.time()
    nominatim_status = is_nominatim_online(geolocator)
    check_end_time = time.time()
    log_to_gui(f"Nominatim服务状态检查耗时：{check_end_time - check_start_time:.2f}秒。")
    if not nominatim_status:
        log_to_gui("Nominatim服务当前不可用。请稍后重试。")
        return nominatim_status

    # 获取图片总数
    total_image_count = len([name for name in os.listdir(input_folder_path) if name.lower().endswith('.jpg')])

    # 处理图片
    for filename in os.listdir(input_folder_path):
        if filename.lower().endswith('.jpg'):
            img_path = os.path.join(input_folder_path, filename)
            try:
                process_image(img_path, filename, tagged_folder_path, no_exif_folder_path)
            except Exception as e:
                log_to_gui(f"处理文件 '{filename}' 时发生错误 - {e}")
                failed_images.append((filename, img_path))
                failed_images_info.append((filename, e))
                failed_img_path = os.path.join(failed_folder_path, f'failed_{filename}')
                copy_file(img_path, failed_img_path)
                failed_images_count += 1
            current_image_index += 1
            processing_images_count += 1
            update_progress_bar(current_image_index / total_image_count)

    # 输出失败图片
    if failed_images:
        log_to_gui("以下文件处理失败:")
        for failed_image, _ in failed_images:
            log_to_gui(f"{failed_image}")
    return nominatim_status

def process_image(img_path, filename, tagged_folder_path, no_exif_folder_path):
    img_start_time = time.time()
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
                log_to_gui(f"处理成功：文件 '{filename}'")
            else:
                raise ValueError("无法获取地理位置信息")
        except Exception as e:
            handle_geolocation_error(e, img_path, filename, tagged_folder_path, lat, lon, time_stamp)
    else:
        log_to_gui(f"没有EXIF信息：{filename}")
        no_exif_img_path = os.path.join(no_exif_folder_path, f'no_exif_{filename}')
        copy_file(img_path, no_exif_img_path)
        no_exif_images_count += 1
    img_end_time = time.time()
    log_to_gui(f"文件 '{filename}' 处理耗时 {img_end_time - img_start_time:.2f}秒")

def handle_geolocation_error(e, img_path, filename, tagged_folder_path, lat, lon, time_stamp):
    if 'HTTPSConnectionPool' in str(e):
        log_to_gui(f"更换user_agent后重试: {filename}")
        geolocator.headers['User-Agent'] = generate_user_agent()
        location = reverse_geocode(geolocator, lat, lon)
        if location:
            reordered_address = reorder_address(location.address)
            img = Image.open(img_path)
            img = rotate_image_based_on_exif(img)
            img_with_text = add_text_to_image(img, time_stamp, reordered_address)
            img_with_text.save(os.path.join(tagged_folder_path, filename))
            log_to_gui(f"重试成功：文件 '{filename}'")
        else:
            raise ValueError("重试后依然无法获取地理位置信息")
    else:
        raise

def select_input_folder():
    global input_folder_path
    input_folder_path = select_folder()
    if input_folder_path:
        input_folder_path_label.config(text=f"输入文件夹：{input_folder_path}")
        log_to_gui(f"选择了输入文件夹：{input_folder_path}")
        return input_folder_path
    return None

def select_output_folder():
    global output_folder_path
    output_folder_path = select_folder()
    if output_folder_path:
        output_folder_path_label.config(text=f"输出文件夹：{output_folder_path}")
        log_to_gui(f"选择了输出文件夹：{output_folder_path}")
        return output_folder_path
    return None

def start_processing():
    global current_image_index, total_image_count, failed_images_info, processing_images_count, failed_images_count, no_exif_images_count
    if input_folder_path and output_folder_path:
        current_image_index = 0
        total_image_count = 0
        failed_images_info = []
        processing_images_count = 0
        failed_images_count = 0
        no_exif_images_count = 0
        threading.Thread(target=process_images, args=(input_folder_path, output_folder_path)).start()
        log_to_gui("开始处理图片...")

def process_images(input_folder_path, output_folder_path):
    global current_image_index, total_image_count, failed_images_info, processing_images_count, failed_images_count, no_exif_images_count
    try:
        nominatim_status = main(input_folder_path, output_folder_path)
        if nominatim_status:
            update_progress_bar(1)
            log_to_gui("处理完成。")
            log_to_gui(f"共处理图片 {total_image_count} 张，其中：")
            log_to_gui(f"    - 处理成功：{total_image_count - failed_images_count - no_exif_images_count} 张")
            log_to_gui(f"    - 处理失败：{failed_images_count} 张")
            log_to_gui(f"    - 无EXIF信息：{no_exif_images_count} 张")
            if failed_images_info:
                log_to_gui("部分图片处理失败，可尝试重新处理。")
        else:
            log_to_gui("Nominatim服务不可用，处理停止。")
    except Exception as e:
        log_to_gui(f"在处理图片过程中发生错误: {e}")
        show_error("处理图片出错", f"在处理图片过程中发生错误: {e}")

def update_progress_bar(value):
    progress_bar['value'] = value * 100

def retry_failed_images():
    global current_image_index, total_image_count, failed_images_info, processing_images_count, failed_images_count, no_exif_images_count
    if input_folder_path and output_folder_path and failed_images_info:
        current_image_index = 0
        total_image_count = len(failed_images_info)
        processing_images_count = 0
        failed_images_count = 0
        no_exif_images_count = 0
        threading.Thread(target=process_failed_images).start()
        log_to_gui("开始重试失败图片...")

def process_failed_images():
    global current_image_index, total_image_count, failed_images_info, processing_images_count, failed_images_count, no_exif_images_count
    new_failed_images_info = []
    for filename, error_info in failed_images_info:
        img_path = os.path.join(input_folder_path, filename)
        try:
            process_image(img_path, filename, os.path.join(output_folder_path, 'tagged_images'), os.path.join(output_folder_path, 'no_exif_images'))
        except Exception as e:
            log_to_gui(f"处理文件 '{filename}' 时发生错误 - {e}")
            new_failed_images_info.append((filename, e))
        current_image_index += 1
        processing_images_count += 1
        update_progress_bar(current_image_index / total_image_count)
    if new_failed_images_info:
        show_info("重试结果", "部分图片重试处理仍失败，请检查。")
        log_to_gui(f"共重试处理 {len(failed_images_info)} 张失败图片，其中：")
        log_to_gui(f"    - 重试成功：{len(failed_images_info) - len(new_failed_images_info)} 张")
        log_to_gui(f"    - 重试失败：{len(new_failed_images_info)} 张")
    else:
        show_info("重试结果", "所有失败图片重试处理成功。")
        log_to_gui("所有失败图片重试处理���功。")

root = Tk()
root.title("图片EXIF信息处理工具")
root.geometry("500x700")

# 结果文本框及垂直滚动条设置
result_text = Text(root, bg='white')
result_text.pack(fill='both', expand=True)

scrollbar = Scrollbar(root, command=result_text.yview)
scrollbar.pack(side='right', fill='y')
result_text.config(yscrollcommand=scrollbar.set)

# 选择输入文件夹和输出文件夹的按钮及路径显示设置
input_select_button = Button(root, text="选择图片文件夹", command=select_input_folder)
input_select_button.pack(pady=5)

input_folder_path_label = Label(root, text="")
input_folder_path_label.pack()

output_select_button = Button(root, text="选择输出文件夹", command=select_output_folder)
output_select_button.pack(pady=5)

output_folder_path_label = Label(root, text="")
output_folder_path_label.pack()

# 开始处理按钮
process_button = Button(root, text="开始处理图片", command=start_processing)
process_button.pack(pady=10)

# 进度条
progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_bar.pack(pady=10)

# 重试失败图片按钮
retry_button = Button(root, text="重试失败图片", command=retry_failed_images)
retry_button.pack(pady=10)

# 添加GitHub图标及链接功能
github_icon_image = Image.open("github_icon.png")
github_icon_image = github_icon_image.resize((32, 32))
github_icon = ImageTk.PhotoImage(github_icon_image)

github_button = Button(root, image=github_icon, command=lambda: webbrowser.open("https://github.com/fjd2004711"))
github_button.pack(side='bottom', pady=10)

root.mainloop()