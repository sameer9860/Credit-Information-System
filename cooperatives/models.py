from django.db import models
from django.utils import timezone


class Cooperative(models.Model):
    """Model representing a cooperative in the system."""
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    contact = models.CharField(max_length=255)  # Can contain phone/email
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Cooperatives'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
