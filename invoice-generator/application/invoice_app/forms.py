# invoice_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Invoice
from django.core.validators import FileExtensionValidator

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    company_name = forms.CharField(
        max_length=255, 
        required=True, 
        label="Company Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your company name'
        })
    )
    
    class Meta:
        model = User
        fields = ('company_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered. Please use a different email.")
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

class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email address.")
        return email

class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        min_length=8,
        label="New Password",
        help_text="Password must be at least 8 characters long."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        label="Confirm New Password"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['company_name', 'pan_number', 'gst_number', 'phone', 'address', 'logo', 'website']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company name'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter PAN number'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter GST number (optional)'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter company address'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter website URL (optional)'}),
        }
        labels = {
            'company_name': 'Company Name *',
            'pan_number': 'PAN Number *',
            'gst_number': 'GST Number',
            'phone': 'Phone Number *',
            'address': 'Address *',
            'logo': 'Company Logo',
            'website': 'Website',
        }
        help_texts = {
            'gst_number': 'Optional',
            'website': 'Optional',
            'logo': 'Upload your company logo (JPG, PNG, GIF, max 2MB)',
        }
    
    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            # Check file size (2MB limit)
            if logo.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Logo file size must be less than 2MB.")
            
            # Check file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            extension = logo.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise forms.ValidationError("Unsupported file format. Please upload JPG, JPEG, or PNG.")
        
        return logo
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and len(phone) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits long.")
        return phone
    
    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if not company_name:
            raise forms.ValidationError("Company name is required.")
        return company_name
    
    def clean_pan_number(self):
        pan_number = self.cleaned_data.get('pan_number')
        if not pan_number:
            raise forms.ValidationError("PAN number is required.")
        return pan_number
    
    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise forms.ValidationError("Address is required.")
        return address

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'date', 'client_name', 'client_email', 'client_phone', 'client_address', 'notes', 'tax_rate']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'client_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'client_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }