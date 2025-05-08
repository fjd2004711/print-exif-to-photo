# app.py
from flask import Flask, request, jsonify, send_file
import os
import shutil
import time
from PIL import Image
from lib.geolocation import geolocator, is_nominatim_online, reverse_geocode
from lib.utils import generate_user_agent
from lib.exif_utils import get_exif_data
from lib.image_utils import rotate_image_based_on_exif, add_text_to_image
from lib.address_utils import reorder_address

app = Flask(__name__)

@app.route('/process_image', methods=['POST'])
def process_image():
    # 获取上传的图片文件
    file = request.files['image']
    if file:
        # 保存上传的图片
        img_path = 'temp_image.jpg'
        file.save(img_path)

        try:
            time_stamp, lat, lon = get_exif_data(img_path)
            if lat and lon:
                location = reverse_geocode(geolocator, lat, lon)
                if location:
                    reordered_address = reorder_address(location.address)
                    img = Image.open(img_path)
                    img = rotate_image_based_on_exif(img)
                    img_with_text = add_text_to_image(img, time_stamp, reordered_address)
                    output_path = 'processed_image.jpg'
                    img_with_text.save(output_path)

                    # 返回处理后的图片
                    return send_file(output_path, mimetype='image/jpeg')
                else:
                    return jsonify({"error": "无法获取地理位置信息"}), 400
            else:
                return jsonify({"error": "没有EXIF信息"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            # 删除临时文件
            if os.path.exists(img_path):
                os.remove(img_path)
            if os.path.exists(output_path):
                os.remove(output_path)

    return jsonify({"error": "未上传图片"}), 400

if __name__ == '__main__':
    app.run(debug=True)