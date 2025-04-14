@echo off
REM 清理过期的ID映射记录

echo 开始清理过期ID映射...
cd /d d:\Anaconda\project\VideoApp
call d:\Anaconda3\envs\videoapp\Scripts\activate.bat
python manage.py clean_id_mappings --days=30
python manage.py verify_id_mappings

echo 清理完成!
pause
