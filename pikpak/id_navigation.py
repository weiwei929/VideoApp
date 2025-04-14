import re
import random
import logging
from functools import lru_cache
from .models import IDMapping
from django.db import transaction, models
from django.utils import timezone

logger = logging.getLogger('pikpak')

class IDNavigationService:
    """
    ID导航系统：管理虚拟ID与实际WebDAV路径的映射关系
    解决路径中特殊字符、Unicode字符和长度限制等问题
    """
    
    @staticmethod
    def get_path(virtual_id):
        """
        根据虚拟ID获取实际路径
        """
        logger.info(f"尝试获取ID的实际路径: {virtual_id}")
        try:
            mapping = IDMapping.objects.get(virtual_id=virtual_id)
            # 更新最后访问时间
            mapping.last_accessed = timezone.now()
            mapping.save(update_fields=['last_accessed'])
            logger.info(f"ID映射找到: {virtual_id} -> {mapping.real_path}")
            return mapping.real_path
        except IDMapping.DoesNotExist:
            if virtual_id == 'dir_0':
                # 根目录特殊处理
                logger.info("使用默认根目录路径: /")
                return '/'
            logger.error(f"找不到ID的映射: {virtual_id}")
            raise ValueError(f"找不到ID为{virtual_id}的映射")
    
    @staticmethod
    @lru_cache(maxsize=128)  # 添加LRU缓存，加速频繁访问的路径查找
    def get_path_cached(virtual_id):
        """
        根据虚拟ID获取实际路径（带缓存）
        """
        return IDNavigationService.get_path(virtual_id)
    
    @staticmethod
    def clear_cache():
        """
        清除路径缓存
        """
        IDNavigationService.get_path_cached.cache_clear()
        logger.info("已清除ID导航系统缓存")
    
    @staticmethod
    def find_or_create_id(real_path, is_directory=False):
        """
        查找或创建指定路径的虚拟ID
        """
        # 清理路径（去除多余斜杠）
        real_path = re.sub(r'//+', '/', real_path)
        if real_path != '/' and real_path.endswith('/'):
            real_path = real_path[:-1]
            
        logger.debug(f"查找或创建路径的ID映射: {real_path}, 是目录: {is_directory}")
            
        # 尝试查找现有映射
        try:
            # 修改为filter而不是get，处理可能的多条记录情况
            existing_mappings = IDMapping.objects.filter(real_path=real_path)
            
            if existing_mappings.exists():
                # 如果存在多条记录，使用第一条并删除其余记录
                if existing_mappings.count() > 1:
                    logger.warning(f"发现路径有多个ID映射: {real_path}, 保留第一个并清理其他")
                    mapping = existing_mappings.first()
                    # 保留第一条，删除其他
                    existing_mappings.exclude(id=mapping.id).delete()
                else:
                    mapping = existing_mappings.first()
                    
                # 更新访问时间
                mapping.last_accessed = timezone.now()
                mapping.save(update_fields=['last_accessed'])
                logger.info(f"使用现有的ID映射: {mapping.virtual_id} -> {real_path}")
                return mapping.virtual_id
            
            # 创建新映射 (使用事务和重试逻辑)
            prefix = 'dir_' if is_directory else 'file_'
            
            max_attempts = 5  # 限制尝试次数，防止无限循环
            for attempt in range(max_attempts):
                try:
                    # 使用锁定超时设置，避免长时间锁定
                    with transaction.atomic(using='default', savepoint=True):
                        # 获取当前最大ID
                        latest = IDMapping.objects.filter(
                            virtual_id__startswith=prefix
                        ).order_by('-virtual_id').first()
                        
                        if latest:
                            # 提取ID数字部分并递增
                            try:
                                last_num = int(latest.virtual_id[len(prefix):].split('_')[0])
                                next_num = last_num + 1
                            except (ValueError, IndexError):
                                # 如果解析失败，生成随机ID
                                next_num = random.randint(1000, 9999)
                        else:
                            next_num = 1
                        
                        # 创建带有时间戳后缀的新ID，以确保唯一性
                        timestamp = int(timezone.now().timestamp()) % 10000
                        new_id = f"{prefix}{next_num}_{timestamp}"
                        
                        # 额外检查确保ID不存在
                        if IDMapping.objects.filter(virtual_id=new_id).exists():
                            # 如果ID依然存在，再添加随机数
                            rand_suffix = random.randint(1000, 9999)
                            new_id = f"{prefix}{next_num}_{timestamp}_{rand_suffix}"
                        
                        # 创建映射记录
                        IDMapping.objects.create(
                            virtual_id=new_id,
                            real_path=real_path,
                            is_directory=is_directory
                        )
                        logger.info(f"成功创建新的ID映射: {new_id} -> {real_path}")
                        return new_id
                except Exception as e:
                    logger.error(f"创建ID映射失败(尝试 {attempt+1}/{max_attempts}): {str(e)}")
                    # 添加短暂延迟，避免连续尝试导致的锁争用
                    import time
                    time.sleep(0.2 * (attempt + 1))
                    
                    if attempt == max_attempts - 1:
                        # 最后一次尝试时，记录详细错误并抛出异常
                        logger.exception("无法创建唯一ID映射，达到最大尝试次数")
                        raise ValueError(f"创建ID映射失败: {str(e)}")
        
        except Exception as e:
            logger.error(f"查找或创建ID映射失败: {str(e)}")
            raise e
    
    @staticmethod
    def clean_old_mappings(days=30):
        """
        清理长时间未访问的映射
        """
        threshold = timezone.now() - timezone.timedelta(days=days)
        logger.info(f"清理{days}天前未访问的ID映射")
        result = IDMapping.objects.filter(last_accessed__lt=threshold).delete()
        logger.info(f"已清理 {result[0]} 条过期映射")
        return result
    
    @staticmethod
    def reset_all_mappings():
        """
        重置所有ID映射，在出现严重错误时使用
        警告：这将清空所有映射记录
        """
        count = IDMapping.objects.all().count()
        logger.warning(f"重置所有ID映射，将删除 {count} 条记录")
        IDMapping.objects.all().delete()
        logger.warning("ID映射重置完成")
        return count
    
    @staticmethod
    def verify_mapping_consistency():
        """
        验证ID映射的一致性
        检查是否存在重复的ID或路径
        """
        # 检查重复ID
        duplicate_ids = (IDMapping.objects.values('virtual_id')
                        .annotate(count=models.Count('virtual_id'))
                        .filter(count__gt=1))
        
        # 检查重复路径
        duplicate_paths = (IDMapping.objects.values('real_path')
                          .annotate(count=models.Count('real_path'))
                          .filter(count__gt=1))
        
        if duplicate_ids.exists():
            logger.error(f"发现重复的虚拟ID: {list(duplicate_ids)}")
        
        if duplicate_paths.exists():
            logger.error(f"发现重复的真实路径: {list(duplicate_paths)}")
            
        return not (duplicate_ids.exists() or duplicate_paths.exists())
