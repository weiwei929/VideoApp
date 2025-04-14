from django.core.management.base import BaseCommand
from pikpak.id_navigation import IDNavigationService

class Command(BaseCommand):
    help = '清理过期的ID映射'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='指定多少天未访问的映射将被删除（默认30天）'
        )

    def handle(self, *args, **options):
        days = options['days']
        self.stdout.write(f'开始清理{days}天未访问的ID映射...')
        
        count, details = IDNavigationService.clean_old_mappings(days)
        
        self.stdout.write(
            self.style.SUCCESS(f'成功清理了{count}条映射记录')
        )
