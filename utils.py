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