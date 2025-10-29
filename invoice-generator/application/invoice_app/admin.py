# invoice_app/admin.py
from django.contrib import admin
from .models import UserProfile, Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client_name', 'date', 'total', 'user')
    list_filter = ('date', 'document_type')
    inlines = [InvoiceItemInline]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'phone', 'gst_number')

admin.site.register(InvoiceItem)