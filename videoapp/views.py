from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

def home(request):
    """首页视图"""
    return render(request, 'home.html')

def video_list(request):
    """视频列表视图"""
    # 将来会从数据库中获取视频列表
    videos = [
        {'id': 1, 'title': '示例视频 1', 'duration': '10:30', 'thumbnail': 'img/thumbnail1.jpg'},
        {'id': 2, 'title': '示例视频 2', 'duration': '5:15', 'thumbnail': 'img/thumbnail2.jpg'},
        {'id': 3, 'title': '示例视频 3', 'duration': '7:45', 'thumbnail': 'img/thumbnail3.jpg'},
    ]
    return render(request, 'videoapp/video_list.html', {'videos': videos})

def video_detail(request, video_id):
    """视频详情页视图"""
    # 将来会从数据库中获取视频详情
    video = {
        'id': video_id,
        'title': f'视频 #{video_id}',
        'description': '这是一个示例视频的描述内容...',
        'duration': '10:30',
        'url': '/static/videos/sample.mp4',
    }
    return render(request, 'videoapp/video_detail.html', {'video': video})

def about(request):
    """关于页面"""
    return render(request, 'videoapp/about.html')
