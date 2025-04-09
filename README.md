# VideoApp

一款功能丰富的个人视频管理和播放系统，支持视频上传、播放和管理。

## 功能特点

- 视频上传和管理
- 自动缩略图生成
- 视频元数据提取（时长、方向）
- 视频流媒体播放
- 支持横屏和竖屏视频
- 系统维护和优化工具

## 技术栈

- Django 5.2
- Python 3.10+
- OpenCV
- Bootstrap 5
- VideoJS 播放器

## 安装指南

1. 克隆仓库
```bash
git clone https://github.com/your-username/VideoApp.git
cd VideoApp
```

2. 使用 Anaconda 环境（推荐）
```bash
# 创建新环境
conda env create -f environment.yml

# 如果环境已存在，可以更新环境
conda env update -f environment.yml --prune

# 激活环境
conda activate videoapp
```

3. 或使用标准虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

4. 准备数据库
```bash
# 创建迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate
```

5. 创建管理员账户
```bash
python manage.py createsuperuser
```

6. 启动开发服务器
```bash
python manage.py runserver
```

## 使用指南

- 访问 `/admin` 管理视频
- 访问 `/videos` 浏览视频库
- 使用 `python tools.py` 运行维护工具

## 版本历史

- 0.2.0 (2025-04-09): 添加自动缩略图生成、视频流媒体、维护工具
- 0.1.0 (2025-04-01): 初始版本

## 许可证

[MIT License](LICENSE)
