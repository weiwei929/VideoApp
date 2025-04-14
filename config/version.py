"""
版本信息管理模块
"""

# 当前版本号
VERSION = '0.50.0'

# 版本发布日期
RELEASE_DATE = '2025-04-14'

# 版本描述
VERSION_DESC = 'PikPak云盘集成版'

def get_version_info():
    """
    获取完整版本信息
    """
    return {
        'version': VERSION,
        'release_date': RELEASE_DATE,
        'description': VERSION_DESC
    }
