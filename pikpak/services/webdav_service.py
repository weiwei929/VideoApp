import requests
import xml.etree.ElementTree as ET
import urllib.parse
from urllib.parse import unquote
import re
import logging

logger = logging.getLogger(__name__)

class WebDAVService:
    """
    WebDAV客户端服务，处理与PikPak WebDAV通信
    """
    
    @staticmethod
    def check_connection(url, username, password):
        """
        验证WebDAV连接
        """
        # 确保URL以斜杠结尾
        if not url.endswith('/'):
            url += '/'
        
        try:
            # 发送OPTIONS请求检查连接
            response = requests.options(
                url,
                auth=(username, password),
                timeout=10
            )
            
            # 检查状态码
            if 200 <= response.status_code < 300:
                # 验证返回的DAV头
                dav_header = response.headers.get('DAV')
                if dav_header and '1' in dav_header:
                    return {'success': True, 'message': '连接成功'}
                else:
                    return {'success': False, 'message': '服务器没有返回有效的DAV头'}
            else:
                return {'success': False, 'message': f'服务器返回错误: {response.status_code}'}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"WebDAV连接失败: {str(e)}")
            return {'success': False, 'message': f'连接失败: {str(e)}'}
    
    @staticmethod
    def list_directory(url, path, username, password):
        """
        列出目录内容
        """
        # 确保URL以斜杠结尾，但path不应该以斜杠开头
        if not url.endswith('/'):
            url += '/'
        
        # 处理路径
        if path.startswith('/'):
            path = path[1:]
        
        # 创建完整URL
        full_url = urllib.parse.urljoin(url, urllib.parse.quote(path))
        if not full_url.endswith('/'):
            full_url += '/'
        
        # 创建PROPFIND请求体
        propfind_body = """
        <?xml version="1.0" encoding="utf-8" ?>
        <D:propfind xmlns:D="DAV:">
            <D:allprop/>
        </D:propfind>
        """
        
        try:
            # 发送PROPFIND请求
            response = requests.request(
                'PROPFIND',
                full_url,
                auth=(username, password),
                headers={'Depth': '1'},
                data=propfind_body,
                timeout=15
            )
            
            # 检查响应状态
            if response.status_code != 207:  # 207是WebDAV多状态响应的标准代码
                logger.error(f"WebDAV列出目录失败: {response.status_code}, {response.text}")
                return {'success': False, 'message': f'服务器返回错误: {response.status_code}'}
            
            # 解析XML响应
            return WebDAVService._parse_propfind_response(response.text, path)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"WebDAV请求失败: {str(e)}")
            return {'success': False, 'message': f'请求失败: {str(e)}'}
        except ET.ParseError as e:
            logger.error(f"WebDAV XML解析失败: {str(e)}")
            return {'success': False, 'message': f'XML解析失败: {str(e)}'}
    
    @staticmethod
    def _parse_propfind_response(xml_text, current_path):
        """
        解析PROPFIND响应XML
        """
        namespaces = {
            'd': 'DAV:'
        }
        
        try:
            root = ET.fromstring(xml_text)
            items = []
            
            # 计算当前路径的长度，用于剔除当前目录
            if not current_path.endswith('/'):
                current_path += '/'
            if current_path == '/':
                current_path_len = 0
            else:
                current_path_len = len(current_path)
            
            # 遍历所有响应
            for response in root.findall('.//d:response', namespaces):
                href = response.find('./d:href', namespaces).text
                href = unquote(href)
                
                # 移除URL部分，只保留路径
                href = href.split('/')
                href = '/'.join([p for p in href if p and not p.startswith('http')])
                
                # 跳过当前目录
                if href == current_path or not href:
                    continue
                
                # 获取属性
                prop = response.find('./d:propstat/d:prop', namespaces)
                
                # 判断是文件还是目录
                resource_type = prop.find('./d:resourcetype', namespaces)
                is_collection = resource_type is not None and resource_type.find('./d:collection', namespaces) is not None
                
                # 获取大小、修改日期等属性
                size_elem = prop.find('./d:getcontentlength', namespaces)
                size = int(size_elem.text) if size_elem is not None and size_elem.text else 0
                
                modified_elem = prop.find('./d:getlastmodified', namespaces)
                modified = modified_elem.text if modified_elem is not None else ''
                
                content_type_elem = prop.find('./d:getcontenttype', namespaces)
                content_type = content_type_elem.text if content_type_elem is not None else ''
                
                # 获取文件名
                name = href.split('/')[-1] if href.split('/')[-1] else href.split('/')[-2]
                
                items.append({
                    'path': href,
                    'name': name,
                    'is_dir': is_collection,
                    'size': size,
                    'modified': modified,
                    'content_type': content_type
                })
            
            return {'success': True, 'items': items}
            
        except Exception as e:
            logger.error(f"解析WebDAV响应失败: {str(e)}")
            return {'success': False, 'message': f'解析响应失败: {str(e)}'}
    
    @staticmethod
    def get_file(url, path, username, password, range_header=None):
        """
        获取文件内容
        支持Range请求，用于视频播放的时间轴拖动
        """
        # 确保URL以斜杠结尾
        if not url.endswith('/'):
            url += '/'
        
        # 处理路径
        if path.startswith('/'):
            path = path[1:]
        
        # 创建完整URL
        full_url = urllib.parse.urljoin(url, urllib.parse.quote(path))
        
        headers = {}
        if range_header:
            headers['Range'] = range_header
            logger.info(f"添加Range请求头: {range_header}")
        
        try:
            logger.info(f"请求WebDAV文件: {full_url}")
            # 发送GET请求
            response = requests.get(
                full_url,
                auth=(username, password),
                headers=headers,
                stream=True,
                timeout=30  # 增加超时时间
            )
            
            # 记录响应信息
            logger.info(f"WebDAV响应状态码: {response.status_code}")
            logger.info(f"WebDAV响应头: {dict(response.headers)}")
            
            # 检查响应状态
            if response.status_code not in [200, 206]:
                logger.error(f"获取文件失败: {response.status_code}")
                return {
                    'success': False, 
                    'message': f'服务器返回错误: {response.status_code}'
                }
            
            # 读取响应头
            resp_headers = {
                'Content-Type': response.headers.get('Content-Type', 'application/octet-stream'),
                'Content-Length': response.headers.get('Content-Length', ''),
                'Accept-Ranges': response.headers.get('Accept-Ranges', 'bytes'),
            }
            
            if response.status_code == 206:
                resp_headers['Content-Range'] = response.headers.get('Content-Range', '')
            
            # 判断是否为图片文件
            content_type = resp_headers['Content-Type']
            is_image = content_type.startswith('image/')
            
            return {
                'success': True, 
                'status_code': response.status_code,
                'headers': resp_headers,
                'stream': response,
                'is_image': is_image  # 添加图片标识
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取文件失败: {str(e)}")
            return {'success': False, 'message': f'获取文件失败: {str(e)}'}
