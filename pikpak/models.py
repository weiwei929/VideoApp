from django.db import models
from django.conf import settings

class PikpakAccount(models.Model):
    """PikPak账户模型"""
    email = models.EmailField('邮箱')
    access_token = models.TextField('访问令牌', blank=True)
    refresh_token = models.TextField('刷新令牌', blank=True)
    token_expiry = models.DateTimeField('令牌过期时间', null=True, blank=True)
    last_login = models.DateTimeField('最近登录', auto_now=True)
    
    class Meta:
        verbose_name = 'PikPak账户'
        verbose_name_plural = 'PikPak账户'
    
    def __str__(self):
        return self.email

class PikpakFile(models.Model):
    """PikPak文件模型"""
    file_id = models.CharField('文件ID', max_length=255)
    name = models.CharField('文件名', max_length=255)
    size = models.BigIntegerField('大小', default=0)
    file_type = models.CharField('类型', max_length=50)
    parent_id = models.CharField('父文件夹ID', max_length=255, blank=True)
    download_url = models.URLField('下载URL', blank=True)
    thumbnail_url = models.URLField('缩略图URL', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = 'PikPak文件'
        verbose_name_plural = 'PikPak文件'
    
    def __str__(self):
        return self.name
