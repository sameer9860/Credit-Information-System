from django.contrib import admin
from .models import Cooperative


@admin.register(Cooperative)
class CooperativeAdmin(admin.ModelAdmin):
    """Admin for Cooperative model."""
    
    list_display = ('name', 'code', 'status', 'contact', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'code', 'contact')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'address', 'contact')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

