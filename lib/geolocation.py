import requests
import json
from geopy.geocoders import Nominatim
from .utils import generate_user_agent

# 读取配置文件
try:
    with open('config/config.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    AMAP_API_KEY = config.get('amap_api_key', '')
except FileNotFoundError:
    print("未找到配置文件 config/config.json，请检查。")
    AMAP_API_KEY = ''
except json.JSONDecodeError:
    print("配置文件 config/config.json 格式错误，请检查。")
    AMAP_API_KEY = ''

geolocator = Nominatim(user_agent=generate_user_agent())

def is_nominatim_online():
    try:
        geolocator.geocode("test")
        return True
    except Exception:
        return False

def reverse_geocode_nominatim(lat, lon):
    try:
        location = geolocator.reverse(f"{lat}, {lon}", language='zh-CN')
        return location
    except Exception as e:
        print(f"使用 Nominatim 进行地址解析时发生错误: {e}")
        return None

def reverse_geocode_amap(lat, lon):
    url = 'https://restapi.amap.com/v3/geocode/regeo'
    params = {
        'key': AMAP_API_KEY,
        'location': f'{lon},{lat}',
        'radius': 1000,
        'extensions': 'base',
        'batch': False,
        'roadlevel': 0
    }
    headers = {
        'User-Agent': generate_user_agent()
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result['status'] == '1' and result['regeocode']:
            address = result['regeocode']['formatted_address']
            return type('Location', (object,), {'address': address})()
        else:
            return None
    except requests.RequestException as e:
        print(f"请求高德地图 API 时发生错误: {e}")
        return None

def reverse_geocode(lat, lon, use_amap=False):
    if use_amap:
        return reverse_geocode_amap(lat, lon)
    else:
        return reverse_geocode_nominatim(lat, lon)