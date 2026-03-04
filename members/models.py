from django.db import models
from django.utils.crypto import get_random_string
import uuid


class Member(models.Model):
    """Model representing a member of a cooperative."""
    
    full_name = models.CharField(max_length=255)
    citizenship_number = models.CharField(max_length=50, unique=True)
    unique_system_id = models.CharField(max_length=20, unique=True, editable=False)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    blacklist_status = models.BooleanField(default=False)
    cooperative = models.ForeignKey(
        'cooperatives.Cooperative',
        on_delete=models.CASCADE,
        related_name='members'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['citizenship_number']),
            models.Index(fields=['unique_system_id']),
            models.Index(fields=['blacklist_status']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.unique_system_id})"

    def save(self, *args, **kwargs):
        if not self.unique_system_id:
            # Generate a unique system ID: MEM-XXXXXX
            while True:
                new_id = f"MEM-{get_random_string(8, allowed_chars='0123456789')}"
                if not Member.objects.filter(unique_system_id=new_id).exists():
                    self.unique_system_id = new_id
                    break
        super().save(*args, **kwargs)
