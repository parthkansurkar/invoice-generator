# invoice_app/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    pan_number = models.CharField(max_length=20)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.company_name

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50)
    date = models.DateField()
    client_name = models.CharField(max_length=255)
    client_email = models.EmailField(blank=True, null=True)
    client_phone = models.CharField(max_length=15, blank=True, null=True)
    client_address = models.TextField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    template_id = models.IntegerField(default=1)
    document_type = models.CharField(max_length=20, choices=[('invoice', 'Invoice'), ('quotation', 'Quotation')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.invoice_number} - {self.client_name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.description