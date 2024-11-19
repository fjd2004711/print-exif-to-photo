# 打印EXIF信息到图片

**简体中文** | [English](README_en.md)

## 介绍

该脚本可以从图片中读取EXIF信息，提取拍摄时间和GPS坐标，并使用这些数据获取详细的地址信息。然后，它会将这些信息添加到图片上，并保存带有地理位置标签和时间戳的新图片。

## 示例图片

![1](https://github.com/fjd2004711/print-exif-to-photo/blob/main/Sample%20image/Sample_image.png)

## 功能

- 读取图片EXIF信息
- 从GPS坐标反解析地址
- 将时间戳和地址添加到图片上
- 支持中文地址格式
- 自动重试和处理失败的操作

## 环境要求

- Python版本: 3.7 或更高
- 操作系统: Windows, macOS, Linux
- 国内用户需要代理环境

## 安装要求

运行此脚本需要安装以下Python模块：

- `PIL`
- `geopy`
- `piexif`
- `datetime`

请使用 `pip install -r requirements.txt` 来安装所需的库。

## 使用方法
**这是此项目的`命令行`版本，我们已为您构建了`EXE`可执行文件，您可以直接 [下载使用](https://github.com/fjd2004711/print-exif-to-photo/releases)，或切换到 [GUI分支](https://github.com/fjd2004711/print-exif-to-photo/tree/GUI) 构建项目。**
1. 确保所有的图片都放在 `images` 文件夹中。
2. 运行脚本:
```
python main.py
```
它会自动创建一个名为 `tagged_images` 的文件夹，并在其中保存标记了时间戳和地址的新图片。
3. 如果处理失败，脚本会自动重试。

### 更改字体及样式

- 将字体文件放入 `fonts`  文件夹。
- 修改`config/style.json`中 `font_path` 的字体路径。 （例如`fonts/example.ttf`，默认为`msyh.ttc`[微软雅黑] ）

#### 配置文件说明

- `font_path`: 使用的字体文件的路径。
- `margin_scale`: 边距比例，定义为图片宽度的一部分。
- `font_size_scale_landscape`: 横向图片的字体大小缩放因子。
- `font_size_scale_portrait`: 纵向图片的字体大小缩放因子。
- `min_font_size`: 文本的最小字体大小。
- `shadow_color`: 文本阴影的颜色。
- `shadow_offset`: 文本阴影的偏移量（以像素为单位）。
- `text_color`: 文本的颜色。
- `spacing`: 行间距，即行与行之间的垂直距离。

### 详细使用教程

[blog.renetxi.com](https://blog.renetxi.com/archives/866)

## 故障排除

如果在图片处理过程中遇到任何问题，如EXIF信息读取失败或地址解析错误，请检查您的图片文件是否损坏，以及网络连接是否正常。

## 贡献

如果您有任何改进建议或功能请求，请创建一个issue或者提交一个拉取请求（pull request）。

## 许可证

本项目采用 GPL-3.0 许可证。详情请见 `LICENSE` 文件。        