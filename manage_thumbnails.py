"""
缩略图管理工具
用法: python manage_thumbnails.py [command]
命令:
  generate - 为没有缩略图的视频生成缩略图
  clear    - 清空所有缩略图
  cleanup  - 清除没有对应视频的孤立缩略图
"""
import os
import sys
import django
import tempfile
import shutil

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.files import File
from vplayer.models import Video

def generate_thumbnails():
    """为所有没有缩略图的视频生成缩略图"""
    try:
        # 导入OpenCV
        import cv2
    except ImportError:
        print("错误: OpenCV未安装")
        print("请执行: pip install opencv-python")
        return False
    
    videos = Video.objects.filter(thumbnail='') | Video.objects.filter(thumbnail__isnull=True)
    print(f"找到 {videos.count()} 个没有缩略图的视频")
    
    for video in videos:
        try:
            print(f"处理视频: {video.title}")
            
            # 获取视频文件路径
            video_path = video.video_file.path
            
            # 打开视频文件
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"  ✗ 无法打开视频文件: {video_path}")
                continue
                
            # 获取视频总帧数和帧率
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # 计算第一秒的帧位置
            frame_pos = min(int(fps), int(total_frames/2))
            
            # 设置要提取的帧位置
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            
            # 读取帧
            ret, frame = cap.read()
            if not ret:
                print(f"  ✗ 无法读取视频帧")
                continue
                
            # 创建缩略图临时文件
            thumbnail_fd, thumbnail_path = tempfile.mkstemp(suffix='.jpg')
            os.close(thumbnail_fd)
            
            # 保存帧为图片
            cv2.imwrite(thumbnail_path, frame)
            
            # 将缩略图添加到模型
            video_filename = os.path.splitext(os.path.basename(video.video_file.name))[0]
            with open(thumbnail_path, 'rb') as f:
                video.thumbnail.save(f"{video_filename}_thumbnail.jpg", File(f))
                
            # 更新视频时长
            duration_seconds = int(total_frames / fps) if fps > 0 else 0
            hours, remainder = divmod(duration_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                video.duration = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                video.duration = f"{minutes:02d}:{seconds:02d}"
                
            # 保存更新
            video.save()
            
            # 清理临时文件
            cap.release()
            try:
                os.unlink(thumbnail_path)
            except:
                pass
                
            print(f"  ✓ 成功为视频 '{video.title}' 生成缩略图")
        
        except Exception as e:
            print(f"  ✗ 处理视频 '{video.title}' 出错: {e}")
    
    print("处理完成")
    return True

def clear_thumbnails():
    """清空所有缩略图"""
    videos = Video.objects.exclude(thumbnail='').exclude(thumbnail__isnull=True)
    count = videos.count()
    
    print(f"找到 {count} 个带有缩略图的视频")
    
    for video in videos:
        try:
            # 删除缩略图文件
            if video.thumbnail and os.path.exists(video.thumbnail.path):
                os.unlink(video.thumbnail.path)
                
            # 清空缩略图字段
            video.thumbnail = None
            video.save()
            
            print(f"  ✓ 已清除视频 '{video.title}' 的缩略图")
        except Exception as e:
            print(f"  ✗ 清除视频 '{video.title}' 的缩略图时出错: {e}")
    
    print("处理完成")
    return True

def cleanup_orphaned_thumbnails():
    """清理没有对应视频的孤立缩略图"""
    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
    
    if not os.path.exists(thumbnail_dir):
        print(f"缩略图目录不存在: {thumbnail_dir}")
        return False
        
    # 获取所有视频的缩略图文件名
    valid_thumbnails = set()
    for video in Video.objects.exclude(thumbnail='').exclude(thumbnail__isnull=True):
        if video.thumbnail:
            valid_thumbnails.add(os.path.basename(video.thumbnail.name))
    
    # 扫描缩略图目录
    orphaned_count = 0
    for filename in os.listdir(thumbnail_dir):
        if filename not in valid_thumbnails:
            file_path = os.path.join(thumbnail_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"  ✓ 已删除孤立缩略图: {filename}")
                    orphaned_count += 1
            except Exception as e:
                print(f"  ✗ 删除缩略图 {filename} 时出错: {e}")
    
    print(f"共删除 {orphaned_count} 个孤立缩略图")
    return True

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
        
    command = sys.argv[1].lower()
    
    if command == 'generate':
        generate_thumbnails()
    elif command == 'clear':
        clear_thumbnails()
    elif command == 'cleanup':
        cleanup_orphaned_thumbnails()
    else:
        print(f"未知命令: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()
