'''
后续步骤:

1. 重启开发服务器:
   python manage.py runserver

2. 进入管理界面(http://127.0.0.1:8000/admin/)并登录

3. 上传新视频:
   - 进入视频管理页面
   - 点击"添加视频"按钮
   - 填写视频标题和描述
   - 选择视频文件
   - 保存

4. 系统将尝试:
   a) 首先使用FFmpeg生成缩略图
   b) 如果FFmpeg不可用，将使用新安装的OpenCV生成缩略图

5. 查看前台视频列表(http://127.0.0.1:8000/videos/)确认视频和缩略图正常显示
'''

'''
问题排查与解决:

1. 添加调试输出到admin.py:
   修改 generate_thumbnail_with_ffmpeg 方法，增加更详细的日志输出:
   ```python
   # 在FFmpeg命令执行后添加详细输出
   print(f"FFmpeg命令执行结果: 返回码={result.returncode}")
   print(f"标准输出: {result.stdout}")
   print(f"标准错误: {result.stderr}")
   ```

2. 检查MEDIA_ROOT目录权限:
   确保Django有权限写入媒体目录。尝试手动创建一个测试文件:
   ```python
   with open('D:\\Anaconda\\project\\VideoApp\\media\\test.txt', 'w') as f:
       f.write('test')
   ```

3. 尝试直接使用OpenCV方法:
   修改admin.py中的save_model方法，直接使用OpenCV而跳过FFmpeg尝试:
   ```python
   def save_model(self, request, obj, form, change):
       """重写保存方法，自动生成缩略图"""
       # 先保存视频本身
       super().save_model(request, obj, form, change)
       
       # 如果上传了新的视频文件，自动生成缩略图
       if 'video_file' in form.changed_data:
           # 直接使用OpenCV生成缩略图
           success = self.generate_thumbnail_with_opencv(request, obj)
           if not success:
               messages.warning(request, "无法生成缩略图，请检查服务器日志")
   ```

4. 手动处理新上传的视频:
   如果自动生成仍然失败，可以使用我们之前创建的脚本手动为新上传的视频生成缩略图:
   ```
   python generate_opencv_thumbnails.py
   ```

5. 检查新上传的视频文件格式:
   某些视频格式可能不被FFmpeg或OpenCV正确识别。请尝试上传一个标准的MP4格式视频。

6. 重启Django开发服务器:
   有时候简单地重启服务器可以解决一些临时问题:
   ```
   CTRL+C (停止当前服务器)
   python manage.py runserver
   ```
'''
