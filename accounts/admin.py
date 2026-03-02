from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with role and cooperative fields."""
    
    list_display = ('username', 'email', 'get_role_display', 'cooperative', 'is_staff', 'is_active')
    list_filter = ('role', 'cooperative', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'cooperative')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'cooperative')
        }),
    )
    ordering = ('-date_joined',)

