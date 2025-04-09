from django.contrib import admin
from .models import Video
from django.contrib import messages
import tempfile
import os
from django.core.files import File

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    fields = ('title', 'description', 'video_file')
    
    def save_model(self, request, obj, form, change):
        """重写保存方法，自动生成缩略图"""
        # 先保存视频本身
        super().save_model(request, obj, form, change)
        
        # 如果上传了新的视频文件，直接使用OpenCV生成缩略图
        if 'video_file' in form.changed_data:
            success = self.generate_thumbnail_with_opencv(request, obj)
            if not success:
                messages.warning(request, "无法使用OpenCV生成缩略图，请检查服务器日志")

    def generate_thumbnail_with_opencv(self, request, obj):
        """使用OpenCV生成缩略图"""
        try:
            try:
                import cv2
                import numpy as np
            except ImportError:
                messages.warning(request, "无法导入OpenCV库，请安装: pip install opencv-python")
                return False

            # 获取视频文件路径
            video_path = obj.video_file.path

            # 打开视频文件
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                messages.warning(request, "无法打开视频文件")
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
                messages.warning(request, "无法读取视频帧")
                return False

            # 创建缩略图临时文件
            thumbnail_fd, thumbnail_path = tempfile.mkstemp(suffix='.jpg')
            os.close(thumbnail_fd)

            # 保存帧为图片
            cv2.imwrite(thumbnail_path, frame)

            # 将缩略图添加到模型
            video_filename = os.path.splitext(os.path.basename(obj.video_file.name))[0]
            with open(thumbnail_path, 'rb') as f:
                obj.thumbnail.save(f"{video_filename}_thumbnail.jpg", File(f))

            # 提取视频时长
            duration_seconds = int(total_frames / fps) if fps > 0 else 0
            hours, remainder = divmod(duration_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                obj.duration = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                obj.duration = f"{minutes:02d}:{seconds:02d}"

            # 保存更新后的视频信息
            obj.save()

            # 清理临时文件和释放资源
            cap.release()
            try:
                os.unlink(thumbnail_path)
            except:
                pass

            messages.success(request, f'已自动为视频"{obj.title}"生成缩略图 (OpenCV)')
            return True

        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.warning(request, f'OpenCV无法生成缩略图: {str(e)}')
            return False
