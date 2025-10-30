# invoice_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Invoice  # Make sure Invoice is imported

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    company_name = forms.CharField(max_length=255, required=True, label="Company Name")
    
    class Meta:
        model = User
        fields = ('company_name', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Use email as username
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name']
            )
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['company_name', 'pan_number', 'gst_number', 'phone', 'address', 'logo', 'website']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice  # This should now work since Invoice is imported above
        fields = ['invoice_number', 'date', 'client_name', 'client_email', 'client_phone', 'client_address', 'notes', 'tax_rate']