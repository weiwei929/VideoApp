"""
配置Git代理
"""
import subprocess
import sys

def setup_proxy():
    # 设置您提供的代理
    proxy_address = "http://127.0.0.1:7897"
    
    print(f"设置Git代理为: {proxy_address}")
    
    # 设置HTTP和HTTPS代理
    subprocess.run(["git", "config", "--global", "http.proxy", proxy_address])
    subprocess.run(["git", "config", "--global", "https.proxy", proxy_address])
    
    # 显示当前配置
    print("\n当前Git代理配置:")
    
    try:
        http_proxy = subprocess.check_output(["git", "config", "--global", "--get", "http.proxy"], 
                                           text=True).strip()
        print(f"HTTP代理: {http_proxy}")
    except subprocess.CalledProcessError:
        print("HTTP代理: 未设置")
        
    try:
        https_proxy = subprocess.check_output(["git", "config", "--global", "--get", "https.proxy"], 
                                            text=True).strip()
        print(f"HTTPS代理: {https_proxy}")
    except subprocess.CalledProcessError:
        print("HTTPS代理: 未设置")
    
    print("\n代理设置完成，现在您可以尝试推送:")
    print("git push -u origin main")

if __name__ == "__main__":
    setup_proxy()
