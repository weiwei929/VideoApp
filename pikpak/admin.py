from django.contrib import admin
from .models import PikpakAccount, PikpakFile, IDMapping

@admin.register(PikpakAccount)
class PikpakAccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'is_token_valid', 'is_webdav_configured')
    search_fields = ('email', 'user__username')
    list_filter = ('token_expiry',)

@admin.register(PikpakFile)
class PikpakFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'mime_type', 'size', 'created_at')
    search_fields = ('name', 'path')
    list_filter = ('mime_type', 'created_at')

@admin.register(IDMapping)
class IDMappingAdmin(admin.ModelAdmin):
    list_display = ('virtual_id', 'real_path', 'is_directory', 'created_at', 'last_accessed')
    search_fields = ('virtual_id', 'real_path')
    list_filter = ('is_directory', 'created_at', 'last_accessed')
