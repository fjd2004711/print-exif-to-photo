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

## 安装要求
运行此脚本需要安装以下Python模块：
- `PIL`
- `geopy`
- `piexif`
- `datetime`

请使用 `pip install -r requirements.txt` 来安装所需的库。

## 使用方法
1. 确保所有的图片都放在 `images` 文件夹中。
2. 运行脚本，它会自动创建一个名为 `tagged_images` 的文件夹，并在其中保存标记了时间戳和地址的新图片。
3. 如果处理失败，脚本会自动重试。

### 更改字体
- 将字体文件放入 `font`  文件夹。
- 修改代码中 `font_path` 的字体路径。

### 详细使用教程
[blog.renetxi.com](https://blog.renetxi.com/archives/866)

## 故障排除
如果在图片处理过程中遇到任何问题，如EXIF信息读取失败或地址解析错误，请检查您的图片文件是否损坏，以及网络连接是否正常。

## 贡献
如果您有任何改进建议或功能请求，请创建一个issue或者提交一个拉取请求（pull request）。

## 许可证
本项目采用 GPL-3.0 许可证。详情请见 `LICENSE` 文件。        