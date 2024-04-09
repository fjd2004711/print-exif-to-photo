from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
from utils import generate_user_agent

geolocator = Nominatim(user_agent=generate_user_agent())


def reverse_geocode(geolocator, lat, lon):
    attempt = 0
    location = None
    while attempt < 3:  # 重试3次
        try:
            location = geolocator.reverse((lat, lon), language='zh', timeout=10)  # 超时设置为10秒
            break
        except GeocoderTimedOut:
            attempt += 1
            time.sleep(5)  # 等待5秒后重试
        except Exception as e:
            print(f"请求地理编码服务时发生错误: {e}")
            break
    return location


def is_nominatim_online(geolocator, timeout=10):
    print("正在检查Nominatim服务状态...")
    try:
        # 在地理编码之前暂停1秒，遵守请求限制
        time.sleep(1)
        location = geolocator.geocode("Eiffel Tower", timeout=timeout)
        if location:
            print("Nominatim 服务状态: 服务在线")
            return True
        else:
            print("Nominatim 服务状态: 未找到位置信息，服务可能存在问题。")
            return False
    except GeocoderTimedOut:
        print("Nominatim 服务状态: 请求超时。")
        return False
    except Exception as e:
        print(f"Nominatim 服务状态: 遇到异常 - {e}")
        return False
