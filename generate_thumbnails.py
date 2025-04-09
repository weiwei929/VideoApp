"""
使用FFmpeg为视频生成缩略图
用法: python generate_thumbnails.py [video_id]
如果不提供video_id，则为所有没有缩略图的视频生成
"""
import os
import sys
import django
import subprocess
import tempfile

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files import File
from vplayer.models import Video

def generate_thumbnail_with_ffmpeg(video):
    """使用FFmpeg为视频生成缩略图"""
    try:
        print(f"为视频 '{video.title}' 生成缩略图...")
        
        # 检查ffmpeg是否可用
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("错误: FFmpeg不可用")
                return False
            print(f"使用FFmpeg版本: {result.stdout.splitlines()[0]}")
        except FileNotFoundError:
            print("错误: FFmpeg未安装或不在PATH中")
            return False
        
        # 获取视频文件路径
        video_path = video.video_file.path
        
        # 创建缩略图临时文件
        thumbnail_fd, thumbnail_path = tempfile.mkstemp(suffix='.jpg')
        os.close(thumbnail_fd)
        
        # 使用ffmpeg截取第1秒的帧作为缩略图
        cmd = [
            'ffmpeg',
            '-i', video_path,  # 输入文件
            '-ss', '00:00:01',  # 截取第1秒
            '-vframes', '1',    # 只截取一帧
            '-q:v', '2',        # 高质量
            thumbnail_path      # 输出文件
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg错误: {result.stderr}")
            return False
        
        # 将缩略图添加到模型
        video_filename = os.path.splitext(os.path.basename(video.video_file.name))[0]
        with open(thumbnail_path, 'rb') as f:
            video.thumbnail.save(f"{video_filename}_thumbnail.jpg", File(f))
        
        # 提取视频时长
        duration_cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        
        duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
        
        if duration_result.returncode == 0:
            try:
                duration_seconds = int(float(duration_result.stdout.strip()))
                hours, remainder = divmod(duration_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                if hours > 0:
                    video.duration = f"{hours}:{minutes:02d}:{seconds:02d}"
                else:
                    video.duration = f"{minutes:02d}:{seconds:02d}"
            except (ValueError, TypeError) as e:
                print(f"无法解析时长: {e}")
                video.duration = "未知"
        else:
            print(f"获取时长失败: {duration_result.stderr}")
            video.duration = "未知"
        
        # 保存更新后的视频信息
        video.save()
        
        # 清理临时文件
        try:
            os.unlink(thumbnail_path)
        except:
            pass
        
        print(f"成功为视频 '{video.title}' 生成缩略图")
        return True
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"生成缩略图时出错: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        # 处理指定ID的视频
        try:
            video_id = int(sys.argv[1])
            try:
                video = Video.objects.get(id=video_id)
                generate_thumbnail_with_ffmpeg(video)
            except Video.DoesNotExist:
                print(f"错误: ID为{video_id}的视频不存在")
        except ValueError:
            print(f"错误: 无效的视频ID '{sys.argv[1]}'")
    else:
        # 处理所有没有缩略图的视频
        videos = Video.objects.filter(thumbnail='') | Video.objects.filter(thumbnail__isnull=True)
        print(f"找到 {videos.count()} 个没有缩略图的视频")
        
        for video in videos:
            generate_thumbnail_with_ffmpeg(video)
        
        print("处理完成")

if __name__ == "__main__":
    main()
