from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from members.models import Member
from cooperatives.models import Cooperative


class Loan(models.Model):

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Cleared', 'Cleared'),
        ('Overdue', 'Overdue'),
    ]

    loan_id = models.AutoField(primary_key=True)

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="loans"
    )

    cooperative = models.ForeignKey(
        Cooperative,
        on_delete=models.CASCADE,
        related_name="loans"
    )

    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Interest rate in %"
    )

    loan_date = models.DateField()

    due_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Active"
    )

    remaining_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.due_date < self.loan_date:
            raise ValidationError("Due date cannot be earlier than loan date.")

    def save(self, *args, **kwargs):

        # initialize remaining balance when loan created
        if not self.remaining_balance:
            self.remaining_balance = self.loan_amount

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan {self.loan_id} - {self.member}"