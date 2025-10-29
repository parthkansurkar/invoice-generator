# invoice_app/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),  # Fixed logout
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('document/choice/', views.document_choice, name='document_choice'),
    path('template/selection/', views.template_selection, name='template_selection'),
    path('invoice/form/', views.invoice_form, name='invoice_form'),
    path('preview/', views.preview, name='preview'),
    path('save/invoice/', views.save_invoice, name='save_invoice'),
]