from django.shortcuts import render, redirect
from django.contrib import messages

def pikpak_home(request):
    """PikPak首页"""
    return render(request, 'pikpak/home.html')

def pikpak_login(request):
    """PikPak登录"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # 这里将来需要添加实际的 PikPak API 调用
        # 目前只是模拟登录成功
        if email and password:
            messages.success(request, "登录成功!")
            return redirect('pikpak:files')
        else:
            messages.error(request, "请输入有效的邮箱和密码")
    
    return render(request, 'pikpak/login.html')

def pikpak_files(request):
    """PikPak文件列表"""
    # 示例文件数据
    files = [
        {'id': 1, 'name': '电影1.mp4', 'size': '1.2 GB', 'type': 'video', 'modified': '2024-05-15'},
        {'id': 2, 'name': '电影2.mp4', 'size': '2.5 GB', 'type': 'video', 'modified': '2024-05-14'},
        {'id': 3, 'name': '电影3.mkv', 'size': '3.7 GB', 'type': 'video', 'modified': '2024-05-13'},
        {'id': 4, 'name': '电视剧1', 'type': 'folder', 'items': 12, 'modified': '2024-05-12'},
    ]
    return render(request, 'pikpak/files.html', {'files': files})

def pikpak_play(request, file_id):
    """PikPak视频播放"""
    # 将来从 PikPak API 获取文件信息
    file = {
        'id': file_id,
        'name': f'视频 {file_id}.mp4',
        'url': '/static/videos/sample.mp4',  # 示例URL
        'size': '1.5 GB',
        'type': 'video/mp4',
    }
    return render(request, 'pikpak/player.html', {'file': file})
