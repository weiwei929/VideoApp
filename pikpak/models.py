from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

class PikpakAccount(models.Model):
    """PikPak账号信息"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)
    
    # WebDAV相关字段
    webdav_url = models.URLField(blank=True, null=True)
    webdav_username = models.CharField(max_length=255, blank=True, null=True)
    webdav_password = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.email
    
    def is_token_valid(self):
        """检查token是否有效"""
        if not self.token_expiry:
            return False
        return self.token_expiry > timezone.now()
    
    def is_webdav_configured(self):
        """检查WebDAV是否配置完成"""
        return bool(self.webdav_url and self.webdav_username and self.webdav_password)

class PikpakFile(models.Model):
    """PikPak文件信息"""
    file_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    path = models.TextField(default='/')  # 添加默认值为'/'
    size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class IDMapping(models.Model):
    """ID与实际WebDAV路径的映射关系"""
    virtual_id = models.CharField(max_length=50, unique=True)
    real_path = models.TextField()
    is_directory = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.virtual_id} -> {self.real_path}"
    
    class Meta:
        indexes = [
            models.Index(fields=['virtual_id']),
            models.Index(fields=['real_path'])
        ]
