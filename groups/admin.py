"""
Group Admin Configuration
"""
from django.contrib import admin
from .models import FileGroup


@admin.register(FileGroup)
class FileGroupAdmin(admin.ModelAdmin):
    """FileGroup Admin"""
    
    list_display = ['name', 'created_by', 'member_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'created_by__username']
    filter_horizontal = ['members']
    
    fieldsets = (
        ('Group Information', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Members', {
            'fields': ('members',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def member_count(self, obj):
        """Display member count"""
        return obj.member_count()
    member_count.short_description = 'Members'
