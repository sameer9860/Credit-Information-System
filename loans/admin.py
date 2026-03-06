from django.contrib import admin
from .models import Loan, Guarantor


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


@admin.register(Guarantor)
class GuarantorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "citizenship_number",
        "loan",
        "member",
        "status"
    )
    list_filter = ("status",)
    search_fields = ("name", "citizenship_number", "loan__loan_id")