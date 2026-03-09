from django import forms
from django.contrib.auth import get_user_model
from cooperatives.models import Cooperative

User = get_user_model()

class StaffCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, help_text="Password must be at least 8 characters.")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    class Meta:
        model = User
        fields = ['username', 'cooperative', 'role', 'password']
        widgets = {
            'role': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Adjust role choices based on who is creating the staff
        if self.request_user and self.request_user.role == 'admin':
            self.fields['role'].choices = [('staff', 'Staff')]
            self.fields['role'].initial = 'staff'
        else:
            self.fields['role'].choices = [('admin', 'Admin'), ('staff', 'Staff')]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        if password and len(password) < 8:
            self.add_error('password', "Password must be at least 8 characters.")
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_first_login = True
        if commit:
            user.save()
        return user


class FirstTimePasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Old Password")
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="New Password", help_text="Must be at least 8 characters.")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm New Password")

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Incorrect old password.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', "New passwords do not match.")
            
        if new_password1 and len(new_password1) < 8:
            self.add_error('new_password1', "Password must be at least 8 characters.")
            
        return cleaned_data
