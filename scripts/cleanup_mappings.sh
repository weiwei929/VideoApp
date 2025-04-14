#!/bin/bash

# 进入项目目录
cd /path/to/VideoApp

# 激活虚拟环境
source /path/to/virtualenv/bin/activate

# 运行清理命令
python manage.py clean_id_mappings --days=30

# 可选：验证映射一致性
python manage.py verify_id_mappings
