from django.contrib import admin
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):

    list_display = (
        "loan_id",
        "member",
        "cooperative",
        "loan_amount",
        "remaining_balance",
        "status",
        "loan_date",
        "due_date"
    )

    list_filter = (
        "status",
        "cooperative",
        "loan_date"
    )

    search_fields = (
        "member__name",
        "loan_id"
    )