import os
import re
import logging
import hashlib
import urllib.parse

logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """
    清理文件名，移除不安全字符
    """
    # 移除不安全字符
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)
    
    # 确保文件名不超过255字符
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        name = name[:255 - len(ext) - 3] + '...'
        filename = name + ext
        
    return filename if filename else 'unnamed'

def generate_path_hash(path):
    """
    为路径生成唯一的哈希值
    """
    return hashlib.md5(path.encode('utf-8')).hexdigest()[:12]

def safe_path_join(*args):
    """
    安全地连接路径，处理编码问题
    """
    path = '/'.join(str(p).strip('/') for p in args if p)
    if not path.startswith('/'):
        path = '/' + path
    return path

def format_size(size_bytes):
    """
    格式化文件大小
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.1f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} GB"
