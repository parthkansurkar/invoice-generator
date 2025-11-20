# invoice_app/models.py
from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    pan_number = models.CharField(max_length=20)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.company_name

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        """Check if OTP is still valid (10 minutes expiry)"""
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(minutes=10)
    
    def mark_used(self):
        self.is_used = True
        self.save()
    
    @classmethod
    def generate_otp(cls, user):
        # Generate a 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        # Invalidate previous OTPs for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        # Create new OTP
        return cls.objects.create(user=user, otp=otp)
    
    def __str__(self):
        return f"OTP for {self.user.email}"

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50)
    date = models.DateField()
    client_name = models.CharField(max_length=255)
    client_email = models.EmailField(blank=True, null=True)
    client_phone = models.CharField(max_length=15, blank=True, null=True)
    client_address = models.TextField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    template_id = models.IntegerField(default=1)
    document_type = models.CharField(max_length=20, choices=[('invoice', 'Invoice'), ('quotation', 'Quotation')], default='invoice')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_totals(self):
        """Calculate subtotal, tax_amount, and total from items"""
        items = self.items.all()
        self.subtotal = sum(item.amount for item in items)
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total = self.subtotal + self.tax_amount
        self.save()
    
    def __str__(self):
        return f"{self.invoice_number} - {self.client_name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        # Auto-calculate amount before saving
        self.amount = self.quantity * self.price
        super().save(*args, **kwargs)
        # Update invoice totals
        self.invoice.calculate_totals()
    
    def __str__(self):
        return self.description