"""
清除Git代理设置
"""
import subprocess

def clear_proxy():
    print("正在清除Git代理设置...")
    
    # 清除HTTP和HTTPS代理
    subprocess.run(["git", "config", "--global", "--unset", "http.proxy"])
    subprocess.run(["git", "config", "--global", "--unset", "https.proxy"])
    
    # 显示当前配置
    print("\n当前Git代理配置:")
    
    try:
        http_proxy = subprocess.check_output(["git", "config", "--global", "--get", "http.proxy"], 
                                           text=True, stderr=subprocess.DEVNULL).strip()
        print(f"HTTP代理: {http_proxy}")
    except subprocess.CalledProcessError:
        print("HTTP代理: 未设置")
        
    try:
        https_proxy = subprocess.check_output(["git", "config", "--global", "--get", "https.proxy"], 
                                            text=True, stderr=subprocess.DEVNULL).strip()
        print(f"HTTPS代理: {https_proxy}")
    except subprocess.CalledProcessError:
        print("HTTPS代理: 未设置")
    
    print("\nGit代理设置已清除")

if __name__ == "__main__":
    clear_proxy()
