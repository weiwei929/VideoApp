from django.core.management.base import BaseCommand
from pikpak.id_navigation import IDNavigationService

class Command(BaseCommand):
    help = '验证ID映射的一致性，检查是否存在重复ID或路径'

    def handle(self, *args, **options):
        self.stdout.write('开始验证ID映射的一致性...')
        
        is_valid = IDNavigationService.verify_mapping_consistency()
        
        if is_valid:
            self.stdout.write(
                self.style.SUCCESS('验证通过：ID映射系统一致性良好')
            )
        else:
            self.stdout.write(
                self.style.ERROR('验证失败：ID映射系统存在数据一致性问题')
            )
            self.stdout.write('建议运行 reset_id_mappings 命令重置映射数据')
