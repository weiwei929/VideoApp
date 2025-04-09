import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache
from vplayer.models import Video

def clear_caches():
    # 清空Django缓存
    print("清空Django缓存...")
    cache.clear()
    
    # 清空媒体文件夹中的缩略图
    thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
    if os.path.exists(thumbnails_dir):
        print(f"清空缩略图目录: {thumbnails_dir}")
        for file in os.listdir(thumbnails_dir):
            file_path = os.path.join(thumbnails_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
                print(f"  删除: {file}")
    
    # 重置视频对象的缩略图字段
    print("重置视频对象的缩略图字段...")
    videos = Video.objects.all()
    for video in videos:
        if video.thumbnail:
            video.thumbnail = None
            video.save()
            print(f"  重置视频 '{video.title}' 的缩略图")
    
    print("缓存清理完成!")

if __name__ == "__main__":
    clear_caches()
