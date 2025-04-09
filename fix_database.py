from django.db import connections
from django.db import connection

def run():
    # 获取数据库连接
    cursor = connection.cursor()
    
    try:
        # 检查并修复表结构
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS new_vplayer_video (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            description TEXT NULL,
            video_file VARCHAR(100) NOT NULL,
            thumbnail VARCHAR(100) NULL,
            duration VARCHAR(10) NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        );
        """)
        
        # 尝试复制数据
        try:
            cursor.execute("""
            INSERT INTO new_vplayer_video 
            (id, title, description, video_file, thumbnail, duration, created_at, updated_at)
            SELECT id, title, description, video_file, thumbnail, duration, created_at, updated_at
            FROM vplayer_video;
            """)
            print("数据复制成功")
        except Exception as e:
            print(f"复制数据失败: {e}")
        
        # 备份旧表并重命名新表
        cursor.execute("DROP TABLE IF EXISTS vplayer_video_backup;")
        cursor.execute("ALTER TABLE vplayer_video RENAME TO vplayer_video_backup;")
        cursor.execute("ALTER TABLE new_vplayer_video RENAME TO vplayer_video;")
        
        print("数据库修复完成")
    except Exception as e:
        print(f"修复数据库时出错: {e}")
        connection.rollback()
        raise
    else:
        connection.commit()

if __name__ == "__main__":
    run()
