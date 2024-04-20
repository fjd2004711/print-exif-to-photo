import random
import string
from datetime import datetime

def generate_user_agent():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

def format_time(time_str):
    try:
        original_format = "%Y:%m:%d %H:%M:%S"
        target_format = "%Y年%m月%d日 %H:%M"
        return datetime.strptime(time_str, original_format).strftime(target_format)
    except ValueError:
        return "时间未知"


def dms_to_dd(dms, ref):
    # 计算度、分、秒的十进制值
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0
    # 根据方向调整正负值
    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds
    return degrees + minutes + seconds
