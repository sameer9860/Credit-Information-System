from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
    """Form for creating and updating members."""
    
    class Meta:
        model = Member
        fields = [
            'full_name', 
            'citizenship_number', 
            'address', 
            'phone', 
            'blacklist_status'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'citizenship_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter citizenship number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'blacklist_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only Super Admin can change blacklist status
        if user and not user.is_superadmin():
            self.fields['blacklist_status'].disabled = True
            self.fields['blacklist_status'].help_text = "Only Super Admins can modify blacklist status."
