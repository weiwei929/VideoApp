from django.contrib import admin
from .models import PikpakAccount, PikpakFile

@admin.register(PikpakAccount)
class PikpakAccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'last_login', 'token_expiry')

@admin.register(PikpakFile)
class PikpakFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'file_type', 'size', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('name',)
