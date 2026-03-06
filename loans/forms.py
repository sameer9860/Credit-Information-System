from django import forms
from .models import Loan, Guarantor

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = [
            "member",
            "cooperative",
            "loan_amount",
            "interest_rate",
            "loan_date",
            "due_date",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Pop 'user' safely
        super().__init__(*args, **kwargs)

        # Example: limit members to user's cooperative if not superadmin
        if self.user and not self.user.is_superadmin():
            self.fields['member'].queryset = self.fields['member'].queryset.filter(cooperative=self.user.cooperative)
            self.fields['cooperative'].widget.attrs['readonly'] = True  # optional: prevent editing

    def clean(self):
        cleaned_data = super().clean()
        loan_date = cleaned_data.get("loan_date")
        due_date = cleaned_data.get("due_date")

        if loan_date and due_date and due_date < loan_date:
            raise forms.ValidationError("Due date must be after loan date")

        return cleaned_data

class GuarantorForm(forms.ModelForm):
    class Meta:
        model = Guarantor
        fields = [
            "name",
            "citizenship_number",
            "loan",
            "member",
            "contact_number",
            "status",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_superadmin():
            # Filter loans to only those in the user's cooperative
            self.fields['loan'].queryset = Loan.objects.filter(cooperative=user.cooperative)
            # Filter members to only those in the user's cooperative
            self.fields['member'].queryset = self.fields['member'].queryset.filter(cooperative=user.cooperative)