"""
VideoApp 版本信息
"""

VERSION = '0.2.0'

CHANGELOG = {
    '0.2.0': {
        'date': '2025-04-09',
        'features': [
            '实现自动缩略图生成功能',
            '添加视频流媒体播放支持',
            '改进视频元数据提取（时长、方向）',
            '添加系统维护和优化工具',
            '优化存储空间使用',
            '修复缩略图生成问题'
        ],
        'dependencies': [
            'OpenCV 替代 MoviePy 用于视频帧处理',
            '使用 Pillow 优化图像处理'
        ]
    },
    '0.1.0': {
        'date': '2025-04-01',
        'features': [
            '初始项目结构',
            '基本视频上传功能',
            '视频播放器集成',
            '基础管理界面'
        ]
    }
}

def get_version():
    return VERSION

def get_changelog():
    return CHANGELOG
