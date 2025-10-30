"""
File Admin Configuration
"""
from django.contrib import admin
from .models import EncryptedFile, FileEncryptionKey


class FileEncryptionKeyInline(admin.TabularInline):
    """Inline display of encryption keys in file admin"""
    model = FileEncryptionKey
    extra = 0
    readonly_fields = ['user', 'created_at']
    can_delete = True


@admin.register(EncryptedFile)
class EncryptedFileAdmin(admin.ModelAdmin):
    """EncryptedFile Admin"""
    
    list_display = ['filename', 'uploaded_by', 'group', 'get_size_display', 'uploaded_at']
    list_filter = ['group', 'uploaded_at']
    search_fields = ['filename', 'uploaded_by__username', 'group__name']
    readonly_fields = ['id', 'uploaded_at', 'file_size', 'nonce', 'tag']
    
    fieldsets = (
        ('File Information', {
            'fields': ('id', 'filename', 'file', 'file_size', 'uploaded_by', 'group')
        }),
        ('Encryption Data', {
            'fields': ('nonce', 'tag'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',)
        }),
    )
    
    inlines = [FileEncryptionKeyInline]
    
    def has_add_permission(self, request):
        """Disable manual file addition (must go through upload view)"""
        return False


@admin.register(FileEncryptionKey)
class FileEncryptionKeyAdmin(admin.ModelAdmin):
    """FileEncryptionKey Admin"""
    
    list_display = ['file', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['file__filename', 'user__username']
    readonly_fields = ['file', 'user', 'encrypted_aes_key', 'created_at']
    
    def has_add_permission(self, request):
        """Disable manual key addition"""
        return False
