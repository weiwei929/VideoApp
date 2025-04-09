from django.db import models
from django.urls import reverse
import os

class Video(models.Model):
    """视频模型"""
    title = models.CharField('标题', max_length=255)
    description = models.TextField('描述', blank=True)
    video_file = models.FileField('视频文件', upload_to='videos/')
    thumbnail = models.ImageField('缩略图', upload_to='thumbnails/', blank=True, null=True)
    duration = models.CharField('时长', max_length=10, blank=True, default="未知")
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '视频'
        verbose_name_plural = '视频'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse('vplayer:video_detail', kwargs={'pk': self.pk})
        
    def video_extension(self):
        """返回视频文件扩展名"""
        name, extension = os.path.splitext(self.video_file.name)
        return extension[1:] if extension else ''
    
    def get_thumbnail_url(self):
        """获取缩略图URL，如果没有则返回默认图片"""
        if self.thumbnail and self.thumbnail.name:
            return self.thumbnail.url
        return '/static/img/default-thumbnail.jpg'
