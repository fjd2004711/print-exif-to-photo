import os
import sys
import shutil
import time
import threading
from PIL import ImageTk
from tkinter import Tk, Button, Label, filedialog, Text, Scrollbar, messagebox, ttk, PhotoImage, Frame
from PIL import Image
from lib.geolocation import geolocator, is_nominatim_online, reverse_geocode
from lib.utils import generate_user_agent
from lib.exif_utils import get_exif_data
from lib.image_utils import rotate_image_based_on_exif, add_text_to_image
from lib.address_utils import reorder_address
import webbrowser

# 全局变量用于存储输入和输出文件夹路径
input_folder_path = None
output_folder_path = None
# 全局变量用于记录当前处理的图片索引和总数
current_image_index = 0
total_image_count = 0
# 全局变量用于存储处理失败的图片信息
failed_images_info = []
# 全局变量用于统计各类图片数量
processing_images_count = 0
failed_images_count = 0
no_exif_images_count = 0


def main(input_folder_path, output_folder_path):
    global current_image_index, total_image_count, processing_images_count, failed_images_count, no_exif_images_count
    tagged_folder_path = os.path.join(output_folder_path, 'tagged_images')
    no_exif_folder_path = os.path.join(output_folder_path, 'no_exif_images')
    failed_folder_path = os.path.join(output_folder_path, 'failed_images')

    # 创建标记图片的文件夹如果它不存在
    if not os.path.exists(tagged_folder_path):
        os.makedirs(tagged_folder_path)
    if not os.path.exists(no_exif_folder_path):
        os.makedirs(no_exif_folder_path)
    if not os.path.exists(failed_folder_path):
        os.makedirs(failed_folder_path)

    # 初始化失败图片列表
    failed_images = []

    # 检查Nominatim服务状态
    check_start_time = time.time()
    nominatim_status = is_nominatim_online(geolocator)
    check_end_time = time.time()
    insert_text(f"Nominatim服务状态检查耗时：{check_end_time - check_start_time:.2f}秒。\n")
    if not nominatim_status:
        insert_text("Nominatim服务当前不可用。请稍后重试。\n")
        return nominatim_status

    # 获取图片总数
    total_image_count = len([name for name in os.listdir(input_folder_path) if name.lower().endswith('.jpg')])

    # 开始处理图片
    for filename in os.listdir(input_folder_path):
        if filename.lower().endswith('.jpg'):
            img_path = os.path.join(input_folder_path, filename)
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
                            insert_text(f"处理成功：文件 '{filename}'\n", 'success')
                            root.after(0, update_progress_bar, current_image_index / total_image_count)
                        else:
                            raise ValueError("无法获取地理位置信息")
                    except Exception as e:
                        if 'HTTPSConnectionPool' in str(e):
                            insert_text(f"更换user_agent后重试: {filename}\n")
                            geolocator.headers['User-Agent'] = generate_user_agent()
                            location = reverse_geocode(geolocator, lat, lon)
                            if location:
                                reordered_address = reorder_address(location.address)
                                img = Image.open(img_path)
                                img = rotate_image_based_on_exif(img)
                                img_with_text = add_text_to_image(img, time_stamp, reordered_address)
                                img_with_text.save(os.path.join(tagged_folder_path, filename))
                                insert_text(f"重试成功：文件 '{filename}'\n", 'success')
                                root.after(0, update_progress_bar, current_image_index / total_image_count)
                            else:
                                raise ValueError("重试后依然无法获取地理位置信息")
                        else:
                            raise
                else:
                    insert_text(f"没有EXIF信息：{filename}\n", 'no_exif')
                    no_exif_img_path = os.path.join(no_exif_folder_path, f'no_exif_{filename}')
                    shutil.copy(img_path, no_exif_img_path)  # 标记没有EXIF信息的图片
                    root.after(0, update_progress_bar, current_image_index / total_image_count)
                    no_exif_images_count += 1  # 更新没有EXIF信息的图片数量
                    continue  # 跳过后续的异常处理
                img_end_time = time.time()
                insert_text(f"文件 '{filename}' 处理耗时 {img_end_time - img_start_time:.2f}秒\n")
            except Exception as e:
                insert_text(f"处理文件 '{filename}' 时发生错误 - {e}\n", 'failure')
                failed_images.append((filename, img_path))
                failed_images_info.append((filename, e))
                failed_img_path = os.path.join(failed_folder_path, f'failed_{filename}')
                shutil.copy(img_path, failed_img_path)  # 复制原始图片到failed_images文件夹并添加前缀
                failed_images_count += 1  # 更新处理失败的图片数量
            current_image_index += 1
            processing_images_count += 1  # 更新正在处理的图片数量
            root.after(0, update_progress_bar, current_image_index / total_image_count)

    # 输出失败的图片
    if failed_images:
        insert_text("以下文件处理失败:\n")
        for failed_image, _ in failed_images:
            insert_text(f"{failed_image}\n", 'failure')
    return nominatim_status


def select_input_folder():
    global input_folder_path
    input_folder_path = filedialog.askdirectory()
    if input_folder_path:
        input_folder_path_label.config(text=f"输入文件夹：{input_folder_path}")
        return input_folder_path
    return None


def select_output_folder():
    global output_folder_path
    output_folder_path = filedialog.askdirectory()
    if output_folder_path:
        output_folder_path_label.config(text=f"输出文件夹：{output_folder_path}")
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
        threading.Thread(target=process_images, args=(input_folder_path, output_folder_path, result_text)).start()


def process_images(input_folder_path, output_folder_path, result_text):
    global current_image_index, total_image_count, failed_images_info, processing_images_count, failed_images_count, no_exif_images_count
    result_text.delete(1.0, 'end')  # 清空结果文本框
    insert_text("正在处理图片，请稍候...\n")  # 添加正在处理的提示信息
    try:
        nominatim_status = main(input_folder_path, output_folder_path)
        if nominatim_status:
            root.after(0, update_progress_bar, 1)
            insert_text("处理完成。\n")
            insert_text(f"共处理图片 {total_image_count} 张，其中：\n")
            insert_text(f"    - 处理成功：{total_image_count - failed_images_count - no_exif_images_count} 张\n")
            insert_text(f"    - 处理失败：{failed_images_count} 张\n")
            insert_text(f"    - 无EXIF信息：{no_exif_images_count} 张\n")
            if failed_images_info:
                insert_text("部分图片处理失败，可尝试重新处理。\n")
        else:
            insert_text("Nominatim服务不可用，处理停止。\n")
    except Exception as e:
        insert_text(f"在处理图片过程中发生错误: {e}\n")
        messagebox.showerror("处理图片出错", f"在处理图片过程中发生错误: {e}")


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


def process_failed_images():
    global current_image_index, total_image_count, failed_images_info, processing_images_count, failed_images_count, no_exif_images_count
    root.after(0, result_text.delete, 1.0, 'end')  # 清空结果文本框
    root.after(0, update_progress_bar, 0)
    new_failed_images_info = []
    for filename, error_info in failed_images_info:
        img_path = os.path.join(input_folder_path, filename)
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
                        img_with_text.save(os.path.join(output_folder_path, 'tagged_images', filename))
                        insert_text(f"重试成功：文件 '{filename}'\n", 'success')
                        root.after(0, update_progress_bar, current_image_index / total_image_count)
                    else:
                        raise ValueError("无法获取地理位置信息")
                except Exception as e:
                    if 'HTTPSConnectionPool' in str(e):
                        insert_text(f"更换user_agent后重试: {filename}\n")
                        geolocator.headers['User-Agent'] = generate_user_agent()
                        location = reverse_geocode(geolocator, lat, lon)
                        if location:
                            reordered_address = reorder_address(location.address)
                            img = Image.open(img_path)
                            img = rotate_image_based_on_exif(img)
                            img_with_text = add_text_to_image(img, time_stamp, reordered_address)
                            img_with_text.save(os.path.join(output_folder_path, 'tagged_images', filename))
                            insert_text(f"重试成功：文件 '{filename}'\n", 'success')
                            root.after(0, update_progress_bar, current_image_index / total_image_count)
                    else:
                        raise ValueError("重试后依然无法获取地理位置信息")
                else:
                    raise ValueError("重试后依然无法获取地理位置信息")
            else:
                insert_text(f"没有EXIF信息：{filename}\n")
                root.after(0, update_progress_bar, current_image_index / total_image_count)
                no_exif_images_count += 1  # 更新没有EXIF信息的图片数量
                continue  # 跳过后续的异常处理
            img_end_time = time.time()
            insert_text(f"文件 '{filename}' 处理耗时 {img_end_time - img_start_time:.2f}秒\n")
        except Exception as e:
            insert_text(f"处理文件 '{filename}' 时发生错误 - {e}\n", 'failure')
            new_failed_images_info.append((filename, e))
        current_image_index += 1
        processing_images_count += 1  # 更新正在处理的图片数量
        root.after(0, update_progress_bar, current_image_index / total_image_count)
    if new_failed_images_info:
        messagebox.showinfo("重试结果", "部分图片重试处理仍失败，请检查。")
        insert_text(f"共重试处理 {len(failed_images_info)} 张失败图片，其中：\n")
        insert_text(f"    - 重试成功：{len(failed_images_info) - len(new_failed_images_info)} 张\n")
        insert_text(f"    - 重试失败：{len(new_failed_images_info)} 张\n")
    else:
        messagebox.showinfo("重试结果", "所有失败图片重试处理成功。")


def insert_text(text, tag=None):
    if tag =='success':
        result_text.tag_config('success', foreground='green')
    elif tag == 'failure':
        result_text.tag_config('failure', foreground='red')
    elif tag == 'no_exif':
        result_text.tag_config('no_exif', foreground='orange')
    result_text.insert('end', text, tag)
    result_text.see('end')


root = Tk()
root.title("图片EXIF信息处理工具")
root.geometry("500x700")

# 结果文本框及垂直滚动条设置
result_text = Text(root, bg='white')
result_text.pack(fill='both', expand=True)

# 插入初始内容示例，这里可以替换为你真正想要显示的内容
# 一级标题样式
result_text.tag_config('h1', font=('Arial', 16, 'bold'), foreground='darkblue')
# 二级标题样式
result_text.tag_config('h2', font=('Arial', 14, 'bold'), foreground='midnightblue')
# 三级标题样式
result_text.tag_config('h3', font=('Arial', 12, 'bold'), foreground='navy')

# 插入一级标题
insert_text("图片EXIF信息处理工具\n", 'h1')
# 插入二级标题
insert_text("一、准备工作\n", 'h2')
insert_text("     请先选择输入和输出文件夹。\n", 'normal')
# 插入二级标题
insert_text("二、处理流程\n", 'h2')
# 插入三级标题
insert_text("（一）开始处理\n", 'h3')
insert_text("     点击开始处理按钮，程序会先检测EXIF解析API运行状态，检测通过后会继续执行。\n", 'normal')
# 插入三级标题
insert_text("（二）处理结果查看\n", 'h3')
insert_text("     处理完成后，可查看处理成功、失败和无EXIF信息的图片数量等结果。\n", 'normal')


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
github_icon_image = Image.open("github_icon.png")  # 替换为你实际的GitHub图标文件路径
github_icon_image = github_icon_image.resize((32, 32))  # 设置你想要的图标大小，这里示例调整为32x32像素

# 将调整后的图像转换为Tkinter可用的PhotoImage对象
github_icon = ImageTk.PhotoImage(github_icon_image)

github_button = Button(root, image=github_icon, command=lambda: webbrowser.open("https://github.com/fjd2004711"))
github_button.pack(side='bottom', pady=10)

root.mainloop()