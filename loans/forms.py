from django import forms
from django.forms import inlineformset_factory
from .models import Loan, Guarantor
from .services import validate_loan_eligibility

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

        # Limit members and hide cooperative if not superadmin
        if self.user and not self.user.is_superadmin():
            self.fields['member'].queryset = self.fields['member'].queryset.filter(cooperative=self.user.cooperative)
            # Remove cooperative field as it should be auto-assigned
            if 'cooperative' in self.fields:
                del self.fields['cooperative']

    def clean(self):
        cleaned_data = super().clean()
        loan_date = cleaned_data.get("loan_date")
        due_date = cleaned_data.get("due_date")
        member = cleaned_data.get("member")

        if loan_date and due_date and due_date < loan_date:
            raise forms.ValidationError("Due date must be after loan date")

        if member:
            try:
                validate_loan_eligibility(member)
            except forms.ValidationError as e:
                # Add the error to the member field
                self.add_error('member', e)

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

GuarantorFormSet = inlineformset_factory(
    Loan, 
    Guarantor, 
    fields=('member', 'name', 'citizenship_number', 'contact_number', 'status'),
    extra=1, 
    can_delete=True
)

GuarantorUpdateFormSet = inlineformset_factory(
    Loan, 
    Guarantor, 
    fields=('member', 'name', 'citizenship_number', 'contact_number', 'status'),
    extra=0, 
    can_delete=True
)