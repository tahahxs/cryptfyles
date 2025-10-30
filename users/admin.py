"""
User Admin Configuration
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""
    
    list_display = ['username', 'email', 'is_staff', 'date_joined', 'has_keys']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Encryption Keys', {'fields': ('encrypted_private_key', 'public_key')}),
    )
    
    def has_keys(self, obj):
        """Display if user has RSA keys"""
        return obj.has_rsa_keys()
    has_keys.boolean = True
    has_keys.short_description = 'Has RSA Keys'
