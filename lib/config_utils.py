import json

def load_config(config_path):
    # 打开配置文件并加载JSON内容
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)
def load_style_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)
