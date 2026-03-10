from django.db import models
from django.utils.crypto import get_random_string
import uuid


class Member(models.Model):
    """Model representing a member of a cooperative."""
    
    full_name = models.CharField(max_length=255)
    citizenship_number = models.CharField(max_length=50, unique=True)
    unique_system_id = models.CharField(max_length=100, unique=True, editable=False)
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
            from django.utils import timezone
            
            current_year = timezone.now().year
            
            try:
                coop_code = self.cooperative.code.upper()
            except Exception:
                coop_code = "MEM"
                
            prefix = f"{coop_code}-{current_year}-"
            
            # Find the latest member with this prefix to determine the next sequence
            latest_member = Member.objects.filter(
                unique_system_id__startswith=prefix
            ).order_by('-unique_system_id').first()
            
            if latest_member:
                try:
                    last_sequence = int(latest_member.unique_system_id.split('-')[-1])
                    new_sequence = last_sequence + 1
                except ValueError:
                    new_sequence = 1
            else:
                new_sequence = 1
                
            self.unique_system_id = f"{prefix}{new_sequence:04d}"
            
            # Ensure uniqueness
            while Member.objects.filter(unique_system_id=self.unique_system_id).exists():
                new_sequence += 1
                self.unique_system_id = f"{prefix}{new_sequence:04d}"
                
        super().save(*args, **kwargs)
