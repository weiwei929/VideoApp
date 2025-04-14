"""
GitHub发布辅助脚本
用于将项目发布到GitHub仓库
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

try:
    from config.version import VERSION
except ImportError:
    VERSION = "unknown"

def run_command(command):
    """运行命令并打印输出"""
    print(f"执行: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"错误: {result.stderr}")
    return result.returncode == 0

def init_repo(repo_url=None):
    """初始化Git仓库"""
    if not os.path.exists(os.path.join(PROJECT_ROOT, '.git')):
        print("初始化Git仓库...")
        os.chdir(PROJECT_ROOT)
        run_command("git init")
        
        # 创建.gitignore文件
        with open(os.path.join(PROJECT_ROOT, '.gitignore'), 'w') as f:
            f.write("""
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS specific
.DS_Store
Thumbs.db

# Project specific
*.bak
uploads/
            """)
    
    if repo_url and not run_command(f"git remote | grep -q origin"):
        print(f"添加远程仓库: {repo_url}")
        run_command(f"git remote add origin {repo_url}")
    
    return True

def create_release(version, message):
    """创建版本提交"""
    print(f"正在创建版本 {version}...")
    os.chdir(PROJECT_ROOT)
    
    # 添加所有文件
    run_command("git add .")
    
    # 提交更改
    run_command(f'git commit -m "版本 {version}: {message}"')
    
    # 添加标签
    run_command(f'git tag -a v{version} -m "版本 {version}"')
    
    print(f"版本 {version} 已创建")
    return True

def push_to_github(version):
    """推送到GitHub"""
    print("正在推送到GitHub...")
    os.chdir(PROJECT_ROOT)
    
    # 推送主分支
    if not run_command("git push -u origin main"):
        # 如果失败，尝试推送到master分支
        run_command("git push -u origin master")
    
    # 推送标签
    run_command(f"git push origin v{version}")
    
    print("推送完成")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='发布项目到GitHub')
    parser.add_argument('--repo', help='GitHub仓库URL')
    parser.add_argument('--message', default=f'发布VideoApp {VERSION}版本', 
                        help='提交信息')
    args = parser.parse_args()
    
    print(f"准备发布 VideoApp {VERSION} 到GitHub...")
    
    if init_repo(args.repo):
        if create_release(VERSION, args.message):
            if push_to_github(VERSION):
                print(f"VideoApp {VERSION} 已成功发布到GitHub!")
    
    print("完成!")
