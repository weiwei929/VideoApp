"""
手动为视频生成缩略图的工具
用法: python thumbnail_generator.py <video_id>
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files import File
from vplayer.models import Video
import tempfile

def generate_thumbnail(video_id):
    try:
        # 获取视频对象
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            print(f"错误: ID为{video_id}的视频不存在")
            return False

        print(f"处理视频: {video.title}")

        # 尝试导入必要的库
        try:
            import moviepy.editor as mp
            from PIL import Image
            import numpy as np
        except ImportError as e:
            print(f"导入错误: {e}")
            print("请确保已安装所需库: pip install moviepy numpy Pillow")
            return False

        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        with video.video_file.open('rb') as f:
            temp_file.write(f.read())
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
        video_filename = os.path.splitext(os.path.basename(video.video_file.name))[0]
        with open(thumbnail_path, 'rb') as f:
            video.thumbnail.save(f"{video_filename}_thumbnail.jpg", File(f))

        # 提取视频时长
        duration_seconds = int(clip.duration)
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            video.duration = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            video.duration = f"{minutes:02d}:{seconds:02d}"

        # 保存更新后的视频信息
        video.save()

        # 清理临时文件
        clip.close()
        os.unlink(temp_file.name)
        if os.path.exists(thumbnail_path):
            os.unlink(thumbnail_path)

        print(f"成功为视频 '{video.title}' 生成缩略图")
        return True
    except Exception as e:
        print(f"生成缩略图时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_id = int(sys.argv[1])
        generate_thumbnail(video_id)
    else:
        print("请提供视频ID作为参数")
        print("用法: python thumbnail_generator.py <video_id>")
