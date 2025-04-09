"""
VideoApp 维护工具
用法: python tools.py [command]

命令:
  cleanup     - 清理临时文件和缓存
  stats       - 显示应用统计信息
  check       - 检查系统依赖
  optimize    - 优化缩略图
  repair      - 尝试修复损坏的视频
  export      - 导出视频信息到CSV
"""
import os
import sys
import django
import shutil
import tempfile  # 添加缺失的导入

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from vplayer.models import Video
from django.core.files import File  # 添加缺失的导入

def cleanup():
    """清理临时文件和缓存"""
    # 清理__pycache__目录
    cleaned = 0
    for root, dirs, files in os.walk(settings.BASE_DIR):
        for dir in dirs:
            if dir == '__pycache__':
                cache_dir = os.path.join(root, dir)
                try:
                    shutil.rmtree(cache_dir)
                    cleaned += 1
                    print(f"已清理: {cache_dir}")
                except Exception as e:
                    print(f"无法清理 {cache_dir}: {e}")
    
    print(f"共清理 {cleaned} 个__pycache__目录")
    
    # 清理.pyc文件
    pyc_count = 0
    for root, dirs, files in os.walk(settings.BASE_DIR):
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = os.path.join(root, file)
                try:
                    os.unlink(pyc_file)
                    pyc_count += 1
                except Exception:
                    pass
    
    print(f"共清理 {pyc_count} 个.pyc文件")

def stats():
    """显示应用统计信息"""
    # 视频统计
    video_count = Video.objects.count()
    total_size = 0
    formats = {}
    
    videos_with_thumbnails = Video.objects.exclude(thumbnail='').exclude(thumbnail__isnull=True).count()
    
    # 添加更多统计信息
    vertical_videos = 0
    horizontal_videos = 0
    
    for video in Video.objects.all():
        if os.path.exists(video.video_file.path):
            size = os.path.getsize(video.video_file.path)
            total_size += size
            
            # 统计格式
            ext = os.path.splitext(video.video_file.name)[1].lower()
            formats[ext] = formats.get(ext, 0) + 1
            
            # 尝试检测视频方向
            try:
                import cv2
                cap = cv2.VideoCapture(video.video_file.path)
                width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                cap.release()
                
                if width and height:
                    if width/height < 0.8:
                        vertical_videos += 1
                    else:
                        horizontal_videos += 1
            except:
                pass
    
    # 显示统计信息
    print("=== VideoApp 统计信息 ===")
    print(f"视频总数: {video_count}")
    print(f"带缩略图视频数: {videos_with_thumbnails}")
    print(f"视频总大小: {total_size / (1024*1024):.2f} MB")
    
    if vertical_videos + horizontal_videos > 0:
        print(f"\n视频方向分布:")
        print(f"  竖屏视频: {vertical_videos}个")
        print(f"  横屏视频: {horizontal_videos}个")
    
    print("\n视频格式分布:")
    for fmt, count in formats.items():
        print(f"  {fmt}: {count}个视频")
        
    # 添加存储占用统计
    thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
    thumbnails_size = 0
    if os.path.exists(thumbnails_dir):
        for file in os.listdir(thumbnails_dir):
            file_path = os.path.join(thumbnails_dir, file)
            if os.path.isfile(file_path):
                thumbnails_size += os.path.getsize(file_path)
                
    print(f"\n缩略图总大小: {thumbnails_size / (1024*1024):.2f} MB")
    print(f"存储总占用: {(total_size + thumbnails_size) / (1024*1024):.2f} MB")

def check_dependencies():
    """检查系统依赖"""
    print("=== 检查系统依赖 ===")
    
    # 检查Python版本
    import platform
    print(f"Python版本: {platform.python_version()}")
    
    # 检查Django版本
    import django
    print(f"Django版本: {django.get_version()}")
    
    # 检查Pillow
    try:
        from PIL import Image
        import PIL
        print(f"Pillow版本: {PIL.__version__}")
    except ImportError:
        print("未找到Pillow库")
    
    # 检查OpenCV
    try:
        import cv2
        print(f"OpenCV版本: {cv2.__version__}")
    except ImportError:
        print("未找到OpenCV库")
    
    # 检查FFmpeg (可选)
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            ffmpeg_ver = result.stdout.split()[2]
            print(f"FFmpeg版本: {ffmpeg_ver}")
        else:
            print("FFmpeg测试失败")
    except Exception:
        print("未找到FFmpeg或无法执行")

def optimize():
    """优化缩略图大小和质量"""
    try:
        from PIL import Image
        print("开始优化缩略图...")
        
        thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
        if not os.path.exists(thumbnails_dir):
            print(f"缩略图目录不存在: {thumbnails_dir}")
            return
            
        total_saved = 0
        processed = 0
        
        for filename in os.listdir(thumbnails_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(thumbnails_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        # 记录原始大小
                        original_size = os.path.getsize(file_path)
                        
                        # 打开并优化图片
                        img = Image.open(file_path)
                        
                        # 调整为标准缩略图大小 (如果太大)
                        if img.width > 640 or img.height > 480:
                            img.thumbnail((640, 480), Image.LANCZOS)
                        
                        # 保存时使用优化的质量设置
                        img.save(file_path, optimize=True, quality=85)
                        
                        # 记录节省的空间
                        new_size = os.path.getsize(file_path)
                        saved = original_size - new_size
                        total_saved += saved
                        
                        if saved > 0:
                            print(f"优化 {filename}: {saved / 1024:.1f}KB 节省")
                        
                        processed += 1
                        
                    except Exception as e:
                        print(f"处理 {filename} 时出错: {e}")
                        
        print(f"\n处理了 {processed} 个缩略图")
        print(f"总共节省: {total_saved / (1024*1024):.2f} MB")
        
    except ImportError:
        print("错误: 未找到PIL库，请安装Pillow")

def repair():
    """尝试修复损坏的视频和缺失的缩略图"""
    print("检查视频和缩略图问题...")
    
    # 检查每个视频
    for video in Video.objects.all():
        # 检查视频文件是否存在
        if not os.path.exists(video.video_file.path):
            print(f"警告: 视频文件缺失: {video.title} ({video.video_file.name})")
            continue
            
        # 检查是否有缩略图
        if not video.thumbnail or not video.thumbnail.name:  # 修复 or 操作符
            print(f"修复: 视频 '{video.title}' 缺少缩略图，尝试生成...")
            try:
                import cv2
                
                # 打开视频文件
                cap = cv2.VideoCapture(video.video_file.path)
                if not cap.isOpened():
                    print(f"  无法打开视频文件: {video.video_file.path}")
                    continue
                    
                # 读取第一帧
                ret, frame = cap.read()
                if not ret:
                    print(f"  无法读取视频帧: {video.video_file.path}")
                    continue
                
                # 创建临时文件保存缩略图
                temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
                os.close(temp_fd)
                
                # 保存帧为图像
                cv2.imwrite(temp_path, frame)
                
                # 将图像添加到视频模型
                video_filename = os.path.splitext(os.path.basename(video.video_file.name))[0]
                with open(temp_path, 'rb') as f:
                    video.thumbnail.save(f"{video_filename}_thumbnail.jpg", File(f))
                    
                # 保存视频记录
                video.save()
                
                # 清理临时文件
                cap.release()
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
                print(f"  ✓ 成功为视频 '{video.title}' 生成缩略图")
                
            except Exception as e:
                print(f"  ✗ 生成缩略图失败: {e}")

def export():
    """导出视频信息到CSV"""
    import csv
    from datetime import datetime
    
    print("导出视频信息到CSV...")
    
    # 创建输出文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(settings.BASE_DIR, f'videos_export_{timestamp}.csv')
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            # 创建CSV写入器
            writer = csv.writer(csvfile)
            
            # 写入表头
            writer.writerow([
                'ID', '标题', '描述', '文件路径', '文件大小(MB)', 
                '时长', '缩略图', '创建时间', '最后更新'
            ])
            
            # 写入数据
            for video in Video.objects.all():
                file_size = 0
                if os.path.exists(video.video_file.path):
                    file_size = os.path.getsize(video.video_file.path) / (1024*1024)
                    
                thumbnail_path = '无缩略图'
                if video.thumbnail and video.thumbnail.name:
                    thumbnail_path = video.thumbnail.name
                    
                writer.writerow([
                    video.id,
                    video.title,
                    video.description[:100] + '...' if len(video.description) > 100 else video.description,
                    video.video_file.name,
                    f'{file_size:.2f}',
                    video.duration,
                    thumbnail_path,
                    video.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    video.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                ])
                
        print(f"视频信息已导出至: {output_file}")
        
    except Exception as e:
        print(f"导出数据时出错: {e}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
        
    command = sys.argv[1].lower()
    
    if command == 'cleanup':
        cleanup()
    elif command == 'stats':
        stats()
    elif command == 'check':
        check_dependencies()
    elif command == 'optimize':
        optimize()
    elif command == 'repair':
        repair()
    elif command == 'export':
        export()
    else:
        print(f"未知命令: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()
