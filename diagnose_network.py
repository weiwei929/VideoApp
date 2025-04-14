"""
GitHub连接诊断工具
"""
import subprocess
import socket
import requests
import sys

def check_dns():
    """检查DNS解析"""
    print("检查DNS解析...")
    try:
        ip = socket.gethostbyname("github.com")
        print(f"✓ github.com 解析到 {ip}")
        return True
    except socket.gaierror:
        print("✗ 无法解析github.com")
        return False

def check_connection():
    """检查连接性"""
    print("\n检查连接...")
    try:
        response = requests.get("https://api.github.com", timeout=5)
        if response.status_code == 200:
            print(f"✓ 可以连接到GitHub API")
            return True
        else:
            print(f"✗ GitHub API返回状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ 无法连接到GitHub API: {e}")
        return False

def check_git_config():
    """检查Git配置"""
    print("\n检查Git配置...")
    
    # 检查代理设置
    try:
        http_proxy = subprocess.check_output(["git", "config", "--get", "http.proxy"], text=True, stderr=subprocess.DEVNULL).strip()
        print(f"HTTP代理设置: {http_proxy if http_proxy else '未设置'}")
    except subprocess.CalledProcessError:
        print("HTTP代理设置: 未设置")
    
    try:
        https_proxy = subprocess.check_output(["git", "config", "--get", "https.proxy"], text=True, stderr=subprocess.DEVNULL).strip()
        print(f"HTTPS代理设置: {https_proxy if https_proxy else '未设置'}")
    except subprocess.CalledProcessError:
        print("HTTPS代理设置: 未设置")
    
    # 检查远程URL
    try:
        remote_url = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
        print(f"远程仓库URL: {remote_url}")
        
        # 判断是HTTPS还是SSH
        if remote_url.startswith("https"):
            print("使用的是HTTPS连接")
        elif remote_url.startswith("git@"):
            print("使用的是SSH连接")
    except subprocess.CalledProcessError:
        print("无法获取远程仓库URL")

def print_solutions():
    """打印可能的解决方案"""
    print("\n可能的解决方案:")
    print("1. 尝试SSH连接:")
    print("   git remote set-url origin git@github.com:weiwei929/VideoApp.git")
    
    print("\n2. 临时关闭SSL验证(不推荐用于敏感仓库):")
    print("   git config --global http.sslVerify false")
    
    print("\n3. 尝试使用GitHub CLI工具:")
    print("   安装GitHub CLI后: gh repo create --source=. --push")
    
    print("\n4. 检查网络环境是否需要设置代理")

def main():
    print("=" * 50)
    print("GitHub连接诊断工具")
    print("=" * 50)
    
    dns_ok = check_dns()
    connection_ok = check_connection()
    check_git_config()
    
    if not dns_ok or not connection_ok:
        print("\n⚠️ 检测到网络连接问题")
    else:
        print("\n✓ 基本网络连接正常，可能是Git配置或GitHub特定问题")
    
    print_solutions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n诊断已取消")
        sys.exit(1)
