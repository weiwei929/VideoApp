from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from .services.webdav_service import WebDAVService
from .services.auth_service import AuthService
from .id_navigation import IDNavigationService
import json
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

def pikpak_home(request):
    """PikPak首页"""
    # 检查是否已配置WebDAV
    credentials = AuthService.get_webdav_credentials_from_session(request)
    is_connected = credentials.get('success', False)
    
    # 清除过期的会话数据
    if is_connected:
        # 检查凭证是否过期 (可选添加)
        last_access = request.session.get('pikpak_last_access', 0)
        current_time = int(timezone.now().timestamp())
        # 如果超过12小时未访问，强制重新登录
        if current_time - last_access > 12 * 3600:  
            if 'webdav_credentials' in request.session:
                del request.session['webdav_credentials']
            is_connected = False
            messages.info(request, "登录会话已过期，请重新连接")
    else:
        # 确保清除会话数据
        if 'webdav_credentials' in request.session:
            del request.session['webdav_credentials']
    
    # 如果已连接，更新最后访问时间
    if is_connected:
        request.session['pikpak_last_access'] = int(timezone.now().timestamp())
    
    # 使用独立模板
    template_name = 'pikpak/standalone_home.html'
    
    return render(request, template_name, {
        'is_connected': is_connected
    })

@ensure_csrf_cookie
def connect_view(request):
    """WebDAV连接设置页面"""
    if request.method == 'POST':
        # 解析请求数据
        webdav_url = request.POST.get('webdav_url', '').strip()
        webdav_username = request.POST.get('webdav_username', '').strip()
        webdav_password = request.POST.get('webdav_password', '').strip()
        
        # 验证输入
        if not all([webdav_url, webdav_username, webdav_password]):
            messages.error(request, '请填写所有WebDAV连接信息')
            return render(request, 'pikpak/standalone_connect.html')
        
        # 测试连接
        result = WebDAVService.check_connection(
            webdav_url, webdav_username, webdav_password
        )
        
        if not result.get('success'):
            messages.error(request, f'连接失败: {result.get("message")}')
            return render(request, 'pikpak/standalone_connect.html')
        
        # 保存凭证
        if request.user.is_authenticated:
            AuthService.save_webdav_credentials(
                request.user, webdav_url, webdav_username, webdav_password
            )
        else:
            AuthService.save_webdav_credentials_to_session(
                request, webdav_url, webdav_username, webdav_password
            )
        
        # 设置最后访问时间
        request.session['pikpak_last_access'] = int(timezone.now().timestamp())
        
        messages.success(request, '连接成功!')
        return redirect('pikpak:browse')
    
    # 如果已经连接，重定向到浏览页面
    credentials = AuthService.get_webdav_credentials_from_session(request)
    if credentials.get('success'):
        return redirect('pikpak:browse')
    
    # 使用独立模板
    return render(request, 'pikpak/standalone_connect.html')

def browse_view(request):
    """浏览WebDAV文件和目录"""
    # 获取凭证
    credentials = AuthService.get_webdav_credentials_from_session(request)
    if not credentials.get('success'):
        messages.warning(request, '请先配置WebDAV连接')
        return redirect('pikpak:connect')
    
    # 获取当前目录ID
    current_id = request.GET.get('id', 'dir_0')  # dir_0 表示根目录
    
    try:
        # 获取实际路径
        real_path = IDNavigationService.get_path(current_id)
        
        # 计算上级目录路径和ID
        parent_id = 'dir_0'  # 默认为根目录
        if real_path != '/' and current_id != 'dir_0':
            parent_path = '/'.join(real_path.rstrip('/').split('/')[:-1])
            if not parent_path:
                parent_path = '/'
            try:
                parent_id = IDNavigationService.find_or_create_id(parent_path, is_directory=True)
                logger.info(f"计算得到上级目录: {parent_path} -> ID: {parent_id}")
            except Exception as e:
                logger.error(f"计算上级目录ID失败: {str(e)}")
                parent_id = 'dir_0'  # 失败时回退到根目录

        # 获取目录内容
        result = WebDAVService.list_directory(
            credentials['webdav_url'],
            real_path,
            credentials['webdav_username'],
            credentials['webdav_password']
        )
        
        if not result.get('success'):
            messages.error(request, f"获取文件列表失败: {result.get('message')}")
            return redirect('pikpak:home')
        
        # 为每个项目生成ID
        items = []
        for item in result.get('items', []):
            try:
                # 跳过当前目录项
                if item['path'] == real_path:
                    continue
                    
                # 构造前端显示所需的数据结构
                virtual_id = IDNavigationService.find_or_create_id(
                    item['path'], 
                    is_directory=item['is_dir']
                )
                
                # 确定文件类型
                if item['is_dir']:
                    item_type = 'folder'
                else:
                    # 检查是否为图片文件
                    file_extension = item['name'].split('.')[-1].lower() if '.' in item['name'] else ''
                    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
                    
                    if 'video' in item.get('content_type', ''):
                        item_type = 'video'
                    elif file_extension in image_extensions:
                        item_type = 'image'
                        logger.info(f"识别到图片文件: {item['name']} - ID: {virtual_id}")
                    else:
                        item_type = 'file'
                
                # 格式化文件大小
                size_str = '文件夹'
                if not item['is_dir']:
                    size = item['size']
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.2f} KB"
                    elif size < 1024 * 1024 * 1024:
                        size_str = f"{size/(1024*1024):.2f} MB"
                    else:
                        size_str = f"{size/(1024*1024*1024):.2f} GB"
                
                items.append({
                    'id': virtual_id,  # 这是关键 - 使用虚拟ID而非真实路径
                    'name': item['name'],
                    'type': item_type,  # 确保type字段正确设置为'image'
                    'size': size_str,
                    'raw_size': item['size'],
                    'modified': item['modified'],
                    'content_type': item.get('content_type', ''),
                    'path': item['path']
                })
            except Exception as e:
                logger.error(f"处理文件项失败: {str(e)}, item: {item}")
                continue
        
        # 准备面包屑导航
        breadcrumbs = [{'id': 'dir_0', 'name': '根目录'}]
        
        # 如果不是根目录，添加父级目录信息
        if current_id != 'dir_0' and real_path != '/':
            # 可以通过路径层次解析添加更多面包屑项
            # 这里简化处理，只显示根目录和当前目录
            try:
                current_path_parts = real_path.strip('/').split('/')
                current_name = current_path_parts[-1] if current_path_parts else '当前目录'
                breadcrumbs.append({'id': current_id, 'name': current_name})
            except Exception as e:
                logger.error(f"构建面包屑导航失败: {str(e)}")
        
        # 使用独立模板并传递额外参数
        return render(request, 'pikpak/standalone_browse.html', {
            'items': items,
            'current_id': current_id,
            'parent_id': parent_id,
            'breadcrumbs': breadcrumbs,
            'is_root': current_id == 'dir_0',  # 标记是否为根目录
            'current_path': real_path  # 添加当前路径参数
        })
        
    except ValueError as e:
        if "找不到ID为" in str(e) and current_id != 'dir_0':
            # 如果ID找不到但不是根目录，尝试回到根目录
            messages.warning(request, f"导航错误，已返回根目录: {str(e)}")
            return redirect('pikpak:browse')  # 回到根目录
        messages.error(request, str(e))
        return redirect('pikpak:home')
    except Exception as e:
        logger.error(f"浏览文件失败: {str(e)}")
        messages.error(request, f"发生错误: {str(e)}")
        return redirect('pikpak:home')

def player_view(request, file_id):
    """视频播放页面"""
    # 获取凭证
    credentials = AuthService.get_webdav_credentials_from_session(request)
    if not credentials.get('success'):
        messages.warning(request, '请先配置WebDAV连接')
        return redirect('pikpak:connect')
    
    try:
        # 获取实际路径
        real_path = IDNavigationService.get_path(file_id)
        
        # 从路径中提取文件名
        filename = real_path.split('/')[-1]
        
        # 使用独立模板
        return render(request, 'pikpak/standalone_player.html', {
            'file_id': file_id,
            'filename': filename,
            'stream_url': f"/pikpak/stream/{file_id}/"
        })
        
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('pikpak:browse')
    except Exception as e:
        logger.error(f"加载播放器失败: {str(e)}")
        messages.error(request, f"发生错误: {str(e)}")
        return redirect('pikpak:browse')

def stream_view(request, file_id):
    """视频流媒体服务
    处理视频文件的流式传输，支持Range请求
    
    必须使用ID导航系统获取实际路径，才能正确处理文件名编码问题
    """
    # 获取凭证
    credentials = AuthService.get_webdav_credentials_from_session(request)
    if not credentials.get('success'):
        return HttpResponseBadRequest('未配置WebDAV连接')
    
    try:
        # 使用ID导航系统获取实际路径 - 这是关键步骤
        real_path = IDNavigationService.get_path(file_id)
        logger.info(f"通过ID导航系统获取到实际路径: {file_id} -> {real_path}")
        
        # 获取Range请求头
        range_header = request.META.get('HTTP_RANGE')
        
        # 添加详细日志
        logger.info(f"处理视频流请求: file_id={file_id}, path={real_path}, range={range_header}")
        
        # 请求文件
        result = WebDAVService.get_file(
            credentials['webdav_url'],
            real_path,
            credentials['webdav_username'],
            credentials['webdav_password'],
            range_header
        )
        
        if not result.get('success'):
            logger.error(f"获取文件流失败: {result.get('message')}")
            return HttpResponseBadRequest(f"获取文件失败: {result.get('message')}")
        
        # 创建流式响应
        response = StreamingHttpResponse(
            result['stream'].iter_content(chunk_size=8192),
            status=result['status_code']
        )
        
        # 设置响应头
        for header, value in result['headers'].items():
            if value:  # 只设置非空值
                response[header] = value
        
        # 记录响应头信息便于调试
        logger.info(f"视频流响应头: {result['headers']}")
        
        return response
        
    except ValueError as e:
        logger.error(f"文件ID错误: {str(e)}")
        return HttpResponseBadRequest(str(e))
    except Exception as e:
        logger.error(f"流媒体服务错误: {str(e)}", exc_info=True)
        return HttpResponseBadRequest(f"服务器错误: {str(e)}")

def ajax_browse(request):
    """AJAX API: 浏览目录
    用于前端异步加载文件列表
    """
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': '仅支持GET请求'})
    
    # 获取凭证
    credentials = AuthService.get_webdav_credentials_from_session(request)
    if not credentials.get('success'):
        return JsonResponse({'success': False, 'message': '未配置WebDAV连接'})
    
    # 获取目录ID
    dir_id = request.GET.get('id', 'dir_0')
    
    try:
        # 获取实际路径
        real_path = IDNavigationService.get_path(dir_id)
        
        # 获取目录内容
        result = WebDAVService.list_directory(
            credentials['webdav_url'],
            real_path,
            credentials['webdav_username'],
            credentials['webdav_password']
        )
        
        if not result.get('success'):
            return JsonResponse({
                'success': False, 
                'message': f"获取文件列表失败: {result.get('message')}"
            })
        
        # 为每个项目生成ID
        items = []
        for item in result.get('items', []):
            virtual_id = IDNavigationService.find_or_create_id(
                item['path'], 
                is_directory=item['is_dir']
            )
            
            # 确定文件类型
            if item['is_dir']:
                item_type = 'folder'
            elif 'video' in item.get('content_type', ''):
                item_type = 'video'
            else:
                item_type = 'file'
            
            items.append({
                'id': virtual_id,
                'name': item['name'],
                'type': item_type,
                'size': item['size'],
                'modified': item['modified'],
                'content_type': item.get('content_type', '')
            })
        
        return JsonResponse({'success': True, 'items': items})
    
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)})
    except Exception as e:
        logger.error(f"AJAX浏览文件失败: {str(e)}")
        return JsonResponse({'success': False, 'message': f"发生错误: {str(e)}"})

def logout_view(request):
    """退出WebDAV连接"""
    # 彻底清除会话数据
    if 'webdav_credentials' in request.session:
        del request.session['webdav_credentials']
    # 添加强制过期所有会话数据的处理
    request.session.flush()
    # 确保所有缓存都被清除
    if hasattr(IDNavigationService, 'clear_cache'):
        IDNavigationService.clear_cache()
    messages.success(request, "已断开WebDAV连接")
    return redirect('pikpak:home')

def image_view(request, file_id):
    """提供图片数据"""
    # 获取凭证
    credentials = AuthService.get_webdav_credentials_from_session(request)
    if not credentials.get('success'):
        return HttpResponseBadRequest('未配置WebDAV连接')
    
    try:
        # 获取实际路径
        real_path = IDNavigationService.get_path(file_id)
        
        # 从文件名确定MIME类型
        file_name = real_path.split('/')[-1]
        content_type = 'image/jpeg'  # 默认MIME类型
        if '.' in file_name:
            ext = file_name.split('.')[-1].lower()
            mime_types = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'bmp': 'image/bmp',
                'webp': 'image/webp',
                'svg': 'image/svg+xml'
            }
            content_type = mime_types.get(ext, 'image/jpeg')
        
        # 请求图片文件
        result = WebDAVService.get_file(
            credentials['webdav_url'],
            real_path,
            credentials['webdav_username'],
            credentials['webdav_password']
        )
        
        if not result.get('success'):
            logger.error(f"获取图片失败: {result.get('message')}")
            return HttpResponseBadRequest(f"获取图片失败: {result.get('message')}")
        
        # 创建流式响应，覆盖WebDAV返回的内容类型
        response = StreamingHttpResponse(
            result['stream'].iter_content(chunk_size=8192),
            status=result['status_code'],
            content_type=content_type  # 使用正确的图片MIME类型
        )
        
        # 关键修改：强制移除Content-Disposition头
        # 不从WebDAV响应中复制Content-Type和Content-Disposition
        for header, value in result['headers'].items():
            if header not in ['Content-Type', 'Content-Disposition'] and value:
                response[header] = value
        
        # 明确设置不要下载而是在浏览器中显示
        response['Content-Disposition'] = 'inline'
        
        # 启用缓存
        response['Cache-Control'] = 'max-age=86400, public'
        
        return response
        
    except ValueError as e:
        logger.error(f"图片ID错误: {str(e)}")
        return HttpResponseBadRequest(str(e))
    except Exception as e:
        logger.error(f"图片服务错误: {str(e)}")
        return HttpResponseBadRequest(f"服务器错误: {str(e)}")