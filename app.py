from flask import Flask, request, jsonify, send_file, render_template, url_for, session, send_from_directory
from flask_socketio import SocketIO, emit
import os
import zipfile
import json
import uuid
from datetime import datetime, timedelta
from main import process_image, NoExifException
from lib.geolocation import geolocator, is_nominatim_online
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用于session加密
app.config['UPLOAD_FOLDER'] = 'images'  # 设置上传文件夹
socketio = SocketIO(app)

BASE_UPLOAD_FOLDER = 'images'
SESSION_FOLDER = 'sessions'

def cleanup_user_data(user_id):
    """清理指定用户的所有数据"""
    user_folder = os.path.join(SESSION_FOLDER, user_id)
    if os.path.exists(user_folder):
        try:
            shutil.rmtree(user_folder)
            print(f"已清理用户 {user_id} 的数据")
        except Exception as e:
            print(f"清理用户 {user_id} 数据时出错: {e}")

def cleanup_old_sessions():
    """清理超过24小时的会话文件夹"""
    if not os.path.exists(SESSION_FOLDER):
        return
    
    current_time = datetime.now()
    for session_id in os.listdir(SESSION_FOLDER):
        session_path = os.path.join(SESSION_FOLDER, session_id)
        if os.path.isdir(session_path):
            # 获取文件夹创建时间
            creation_time = datetime.fromtimestamp(os.path.getctime(session_path))
            # 如果超过24小时，删除文件夹
            if (current_time - creation_time).total_seconds() > 24 * 3600:
                cleanup_user_data(session_id)

def create_user_dir():
    user_id = session.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
    
    # 创建用户主目录
    user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
    os.makedirs(user_dir, exist_ok=True)
    
    # 创建子目录
    success_dir = os.path.join(user_dir, 'success')
    failed_dir = os.path.join(user_dir, 'failed')
    no_exif_dir = os.path.join(user_dir, 'no_exif')
    
    os.makedirs(success_dir, exist_ok=True)
    os.makedirs(failed_dir, exist_ok=True)
    os.makedirs(no_exif_dir, exist_ok=True)
    
    return user_dir, success_dir, failed_dir, no_exif_dir

@app.route('/images/<user_id>/<category>/<filename>')
def serve_image(user_id, category, filename):
    try:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], user_id, category, filename)
        print(f"Serving image from: {image_path}")  # 添加调试日志
        return send_from_directory(
            os.path.join(app.config['UPLOAD_FOLDER'], user_id, category),
            filename
        )
    except Exception as e:
        print(f"获取图片时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/process-images', methods=['POST'])
def process_images():
    try:
        # 创建用户目录
        user_dir, success_dir, failed_dir, no_exif_dir = create_user_dir()
        
        # 获取表单数据
        api_type = request.form.get('api_type', 'nominatim')
        api_key = request.form.get('api_key', '')
        font_family = request.form.get('font_family', 'msyh.ttc')
        font_size = int(request.form.get('font_size', 0))
        text_color = request.form.get('text_color', '#ffffff')
        shadow_color = request.form.get('shadow_color', '#000000')
        shadow_offset = int(request.form.get('shadow_offset', 2))
        spacing = int(request.form.get('spacing', 30))
        print_position = request.form.get('print_position', 'bottom-right')
        
        # 获取上传的图片
        images = request.files.getlist('images')
        if not images:
            return jsonify({'error': '没有上传图片'}), 400
        
        # 处理每张图片
        success_count = 0
        fail_count = 0
        no_exif_count = 0
        
        for idx, image in enumerate(images):
            try:
                filename = secure_filename(image.filename)
                original_path = os.path.join(user_dir, filename)
                image.save(original_path)
                if hasattr(image, 'close'):
                    image.close()
                # 调用处理函数
                result = process_image(
                    original_path,
                    api_key,           # amap_api_key
                    api_type,          # nominatim_api
                    font_size,
                    print_position,
                    {
                        'tagged': success_dir,
                        'failed': failed_dir,
                        'no_exif': no_exif_dir
                    },
                    font_family=font_family,
                    text_color=text_color,
                    shadow_color=shadow_color,
                    shadow_offset=shadow_offset,
                    spacing=spacing
                )
                success_count += 1
            except NoExifException:
                no_exif_count += 1
            except Exception as e:
                print(f"处理图片 {image.filename} 时出错: {str(e)}")
                fail_count += 1
            finally:
                progress = int((idx + 1) / len(images) * 100)
                socketio.emit('progress', {'progress': progress})
        
        return jsonify({
            'success': success_count,
            'fail': fail_count,
            'no_exif': no_exif_count
        })
    except Exception as e:
        print(f"处理图片时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-images')
def get_images():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '未找到用户ID'}), 400
        
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
        success_dir = os.path.join(user_dir, 'success')
        failed_dir = os.path.join(user_dir, 'failed')
        no_exif_dir = os.path.join(user_dir, 'no_exif')
        
        def get_images_from_dir(directory):
            images = []
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        images.append({
                            'name': filename,
                            'path': f'/images/{user_id}/{os.path.basename(directory)}/{filename}'
                        })
            return images
        
        result = {
            'success': get_images_from_dir(success_dir),
            'failed': get_images_from_dir(failed_dir),
            'no_exif': get_images_from_dir(no_exif_dir)
        }
        print(f"返回的图片列表: {result}")  # 添加调试日志
        return jsonify(result)
    except Exception as e:
        print(f"获取图片列表时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download-processed', methods=['GET'])
def download_processed():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "未找到用户会话"}), 404

    user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
    zip_filename = f'processed_images_{user_id}.zip'
    zip_path = os.path.join(user_dir, zip_filename)

    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for category in ['success', 'failed', 'no_exif']:
                category_dir = os.path.join(user_dir, category)
                if os.path.exists(category_dir):
                    for file in os.listdir(category_dir):
                        file_path = os.path.join(category_dir, file)
                        zipf.write(file_path, arcname=f'{category}/{file}')

        def delete_zip():
            try:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                    print(f"已删除压缩包: {zip_path}")
            except Exception as e:
                print(f"删除压缩包时出错: {e}")

        socketio.start_background_task(delete_zip)
        return send_file(zip_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear-data', methods=['POST'])
def clear_data():
    """清理当前用户的所有数据"""
    if 'user_id' in session:
        cleanup_user_data(session['user_id'])
        return jsonify({"message": "数据已清理"})
    return jsonify({"error": "未找到用户会话"}), 404

@app.route('/check-api', methods=['GET'])
def check_api():
    api_type = request.args.get('api_type', 'nominatim')
    if api_type == 'nominatim':
        return jsonify({'status': is_nominatim_online(geolocator)})
    return jsonify({'status': True})  # 其他API类型需要实现检查

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('progress')
def handle_progress(data):
    try:
        emit('progress', data, broadcast=True)
    except Exception as e:
        print(f"发送进度更新时出错: {e}")

if __name__ == '__main__':
    # 确保会话文件夹存在
    os.makedirs(SESSION_FOLDER, exist_ok=True)
    # 清理旧会话
    cleanup_old_sessions()
    socketio.run(app, debug=True)

