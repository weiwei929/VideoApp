#!/bin/bash
# 设置正确的Git代理配置

# 设置HTTP和HTTPS代理
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897

# 验证代理设置
echo "当前Git代理配置:"
git config --global --get http.proxy
git config --global --get https.proxy

echo "代理设置完成，现在可以尝试推送:"
echo "git push -u origin main"
