import os  # 添加这一行以导入os模块
from pathlib import Path  # 如果使用Path对象

# 如果使用Path (Django 3.1+)
BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 其他应用...
    'vplayer',
    'users',
    'pikpak',  # 确保这一行已添加
]

# 确保BASE_DIR已定义 (如果这行不存在)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 确保这些设置存在
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]