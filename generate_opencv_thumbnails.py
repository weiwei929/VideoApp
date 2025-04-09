import os
import django
import sys
import tempfile

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files import File
from vplayer.models import Video

def generate_thumbnail_with_opencv(video):
    """使用OpenCV为视频生成缩略图"""
    try:
        print(f"为视频 '{video.title}' 生成缩略图...")
        
        try:
            import cv2
            import numpy as np
        except ImportError:
            print("错误: 无法导入OpenCV库")
            return False
            
        # 获取视频文件路径
        video_path = video.video_file.path
        
        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("错误: 无法打开视频文件")
            return False
            
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
            print("错误: 无法读取视频帧")
            return False
            
        # 创建缩略图临时文件
        thumbnail_fd, thumbnail_path = tempfile.mkstemp(suffix='.jpg')
        os.close(thumbnail_fd)
        
        # 保存帧为图片
        cv2.imwrite(thumbnail_path, frame)
        
        # 将缩略图添加到模型
        video_filename = os.path.splitext(os.path.basename(video.video_file.name))[0]
        with open(thumbnail_path, 'rb') as f:
            video.thumbnail.save(f"{video_filename}_thumbnail.jpg", File(f))
            
        # 提取视频时长
        duration_seconds = int(total_frames / fps) if fps > 0 else 0
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            video.duration = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            video.duration = f"{minutes:02d}:{seconds:02d}"
            
        # 保存更新后的视频信息
        video.save()
        
        # 清理临时文件和释放资源
        cap.release()
        try:
            os.unlink(thumbnail_path)
        except:
            pass
            
        print(f"  ✓ 成功为视频 '{video.title}' 生成缩略图")
        return True
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"  ✗ 生成缩略图失败: {e}")
        return False

def main():
    # 查找所有没有缩略图的视频
    videos = Video.objects.filter(thumbnail='') | Video.objects.filter(thumbnail__isnull=True)
    print(f"找到 {videos.count()} 个没有缩略图的视频")
    
    for video in videos:
        generate_thumbnail_with_opencv(video)
        
    print("处理完成")

if __name__ == "__main__":
    main()
