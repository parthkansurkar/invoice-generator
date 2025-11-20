# invoice_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('landing/', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Password reset URLs
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),
    
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('document/choice/', views.document_choice, name='document_choice'),
    path('template/selection/', views.template_selection, name='template_selection'),
    path('invoice/form/', views.invoice_form, name='invoice_form'),
    path('preview/', views.preview, name='preview'),
    path('save/invoice/', views.save_invoice, name='save_invoice'),
    path('invoice/history/', views.invoice_history, name='invoice_history'),
]