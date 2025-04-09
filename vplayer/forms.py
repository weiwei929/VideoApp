from django import forms
from .models import Video
from django.conf import settings
import os

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        # 移除 thumbnail 字段，不再允许手动上传
        fields = ['title', 'description', 'video_file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        
    def clean_video_file(self):
        video = self.cleaned_data.get('video_file')
        if video:
            # 检查文件扩展名
            ext = os.path.splitext(video.name)[1][1:].lower()
            if ext not in settings.VIDEO_ALLOWED_EXTENSIONS:
                allowed_exts = ', '.join(settings.VIDEO_ALLOWED_EXTENSIONS)
                raise forms.ValidationError(f'不支持的视频格式。请上传以下格式的视频: {allowed_exts}')
            
            # 检查文件大小
            if video.size > settings.VIDEO_MAX_SIZE:
                max_size_mb = settings.VIDEO_MAX_SIZE / (1024 * 1024)
                raise forms.ValidationError(f'视频文件过大，最大允许 {max_size_mb} MB')
        
        return video
