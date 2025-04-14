from django.core.management.base import BaseCommand
from pikpak.id_navigation import IDNavigationService

class Command(BaseCommand):
    help = '重置所有ID映射，清空映射表'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制执行，不提示确认'
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        if not force:
            confirm = input("警告：此操作将删除所有ID映射记录。继续操作? (y/N): ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('操作已取消'))
                return
        
        try:
            count = IDNavigationService.reset_all_mappings()
            self.stdout.write(
                self.style.SUCCESS(f'成功清除了{count}条ID映射记录')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'清除ID映射记录失败: {str(e)}')
            )
