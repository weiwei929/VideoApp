from django.core.management.base import BaseCommand
from pikpak.models import IDMapping
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '清理重复的ID映射记录'

    def handle(self, *args, **options):
        self.stdout.write('开始清理重复的ID映射...')
        
        # 获取所有唯一路径
        unique_paths = IDMapping.objects.values_list('real_path', flat=True).distinct()
        cleaned_count = 0
        
        for path in unique_paths:
            # 查找每个路径的所有映射
            mappings = IDMapping.objects.filter(real_path=path).order_by('id')
            
            if mappings.count() > 1:
                # 保留最早的一条记录
                first_mapping = mappings.first()
                # 删除其他记录
                delete_count = mappings.exclude(id=first_mapping.id).delete()[0]
                cleaned_count += delete_count
                self.stdout.write(f'路径"{path}"有{delete_count+1}条记录，保留ID为{first_mapping.virtual_id}的记录，删除{delete_count}条')
        
        self.stdout.write(self.style.SUCCESS(f'清理完成，共删除了{cleaned_count}条重复记录'))
