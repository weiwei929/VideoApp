from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Video
from .forms import VideoUploadForm
import os
import tempfile
from django.core.files import File
import traceback
from django.http import FileResponse, Http404
from django.views.decorators.http import condition
import datetime

# 视频最大缓冲区大小(1MB)
BUFFER_SIZE = 1024 * 1024

def etag_func(request, video_id):
    """生成ETag，用于缓存控制"""
    try:
        video = Video.objects.get(pk=video_id)
        return f"{video_id}-{os.path.getmtime(video.video_file.path)}"
    except (Video.DoesNotExist, OSError):
        return None

def last_modified_func(request, video_id):
    """获取最后修改时间，用于缓存控制"""
    try:
        video = Video.objects.get(pk=video_id)
        return datetime.datetime.fromtimestamp(os.path.getmtime(video.video_file.path))
    except (Video.DoesNotExist, OSError):
        return None

@condition(etag_func=etag_func, last_modified_func=last_modified_func)
def stream_video(request, video_id):
    """流式传输视频文件，支持断点续传"""
    try:
        video = get_object_or_404(Video, pk=video_id)
        
        # 获取文件路径
        file_path = video.video_file.path
        
        # 创建文件响应，移除 buffer_size 参数
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='video/mp4',
            filename=os.path.basename(file_path),
            as_attachment=False,
        )
        
        return response
    except Exception as e:
        # 记录日志但不显示堆栈跟踪
        print(f"视频流错误: {str(e)}")
        raise Http404("视频不可用")

def generate_thumbnail_from_video(video_instance, video_file=None):
    """从视频文件生成缩略图和提取时长"""
    try:
        # 动态导入 moviepy，避免全局依赖
        import moviepy.editor as mp
        from PIL import Image
        import numpy as np
        
        # 如果没有提供视频文件，则使用模型中的文件
        if video_file is None:
            video_file = video_instance.video_file
            
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        for chunk in video_file.chunks():
            temp_file.write(chunk)
        temp_file.close()
        
        print(f"临时文件创建成功: {temp_file.name}")
        
        # 读取视频文件
        clip = mp.VideoFileClip(temp_file.name)
        
        # 获取第1秒的帧作为缩略图
        screenshot_time = min(1, clip.duration / 2)
        thumbnail_frame = clip.get_frame(screenshot_time)
        
        # 保存帧为临时图片
        thumbnail_path = f"{temp_file.name}_thumb.jpg"
        Image.fromarray(thumbnail_frame.astype(np.uint8)).save(thumbnail_path)
        
        print(f"缩略图文件创建成功: {thumbnail_path}")
        
        # 将临时图片添加到模型
        video_filename = os.path.splitext(os.path.basename(video_instance.video_file.name))[0]
        with open(thumbnail_path, 'rb') as f:
            video_instance.thumbnail.save(f"{video_filename}_thumbnail.jpg", File(f))
        
        # 提取视频时长
        duration_seconds = int(clip.duration)
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            video_instance.duration = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            video_instance.duration = f"{minutes}:{seconds:02d}"
        
        # 清理临时文件
        clip.close()
        os.unlink(temp_file.name)
        if os.path.exists(thumbnail_path):
            os.unlink(thumbnail_path)
        
        print(f"缩略图生成成功，已保存为 {video_instance.thumbnail.name}")
        return True
    except ImportError:
        print("生成缩略图失败: moviepy 库未安装")
        return False
    except Exception as e:
        print(f"生成缩略图失败: {e}")
        traceback.print_exc()
        return False

def home(request):
    """首页视图"""
    return render(request, 'home.html')

class VideoListView(ListView):
    """视频列表视图"""
    model = Video
    template_name = 'vplayer/video_list.html'
    context_object_name = 'videos'
    paginate_by = 12

class VideoDetailView(DetailView):
    """视频详情视图"""
    model = Video
    template_name = 'vplayer/video_detail.html'
    context_object_name = 'video'

def about(request):
    """关于页面"""
    return render(request, 'vplayer/about.html')

class VideoUploadView(CreateView):
    model = Video
    form_class = VideoUploadForm
    template_name = 'vplayer/video_upload.html'
    success_url = reverse_lazy('vplayer:video_list')
    
    def form_valid(self, form):
        video = form.save(commit=False)
        
        # 设置默认时长
        video.duration = "未知"
        
        # 先保存视频文件以便能够访问它
        video.save()
        
        # 从视频生成缩略图
        success = generate_thumbnail_from_video(video)
        if not success:
            messages.warning(self.request, "无法从视频生成缩略图，将使用默认缩略图")
        
        # 保存更新后的视频（包含缩略图和时长）
        video.save()
        
        messages.success(self.request, f'视频 "{video.title}" 上传成功！')
        return super().form_valid(form)

class VideoUpdateView(UpdateView):
    model = Video
    form_class = VideoUploadForm
    template_name = 'vplayer/video_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('vplayer:video_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        video = form.save(commit=False)
        
        # 如果上传了新的视频文件，从视频生成新缩略图
        if 'video_file' in form.changed_data:
            video.save()  # 先保存视频文件
            success = generate_thumbnail_from_video(video)
            if not success:
                messages.warning(self.request, "无法从视频生成新缩略图")
        
        video.save()
        messages.success(self.request, f'视频 "{form.instance.title}" 已更新！')
        return super().form_valid(form)

class VideoDeleteView(DeleteView):
    model = Video
    template_name = 'vplayer/video_confirm_delete.html'
    success_url = reverse_lazy('vplayer:video_list')
    
    def delete(self, request, *args, **kwargs):
        video = self.get_object()
        messages.success(request, f'视频 "{video.title}" 已删除！')
        return super().delete(request, *args, **kwargs)