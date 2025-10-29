# invoice_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm
from .models import UserProfile, Invoice, InvoiceItem

# Template data with different designs
TEMPLATES_DATA = {
    1: {
        'name': 'Modern Blue',
        'primary_color': '#4361ee',
        'secondary_color': '#3a0ca3',
        'background': 'linear-gradient(135deg, #4361ee, #3a0ca3)',
        'style': 'modern'
    },
    2: {
        'name': 'Professional Green',
        'primary_color': '#2a9d8f',
        'secondary_color': '#264653',
        'background': 'linear-gradient(135deg, #2a9d8f, #264653)',
        'style': 'professional'
    },
    3: {
        'name': 'Elegant Purple',
        'primary_color': '#7209b7',
        'secondary_color': '#3a0ca3',
        'background': 'linear-gradient(135deg, #7209b7, #3a0ca3)',
        'style': 'elegant'
    },
    4: {
        'name': 'Warm Orange',
        'primary_color': '#f77f00',
        'secondary_color': '#d62828',
        'background': 'linear-gradient(135deg, #f77f00, #d62828)',
        'style': 'warm'
    },
    5: {
        'name': 'Corporate Gray',
        'primary_color': '#495057',
        'secondary_color': '#212529',
        'background': 'linear-gradient(135deg, #495057, #212529)',
        'style': 'corporate'
    },
    6: {
        'name': 'Creative Pink',
        'primary_color': '#f72585',
        'secondary_color': '#b5179e',
        'background': 'linear-gradient(135deg, #f72585, #b5179e)',
        'style': 'creative'
    }
}

def landing(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Auto-login after registration
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Account created successfully! Please complete your profile.')
                return redirect('profile_setup')
            else:
                messages.error(request, 'Auto-login failed. Please login manually.')
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    """Dashboard view for authenticated users"""
    # Use get_or_create to ensure profile always exists
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'company_name': 'Your Company',
            'phone': 'Not provided',
            'address': 'Not provided',
            'pan_number': 'Not provided'
        }
    )
    
    # If profile was just created or is incomplete, redirect to setup
    if created or not profile.company_name or profile.company_name == 'Your Company' or not profile.phone or profile.phone == 'Not provided':
        messages.info(request, 'Please complete your business profile setup.')
        return redirect('profile_setup')
    
    # Calculate statistics
    try:
        total_invoices = Invoice.objects.filter(user=request.user).count()
        invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')[:5]
        total_revenue = sum([invoice.total for invoice in Invoice.objects.filter(user=request.user)]) if invoices else 0
    except:
        total_invoices = 0
        invoices = []
        total_revenue = 0
    
    pending_invoices = total_invoices  # Placeholder
    paid_invoices = 0  # Placeholder
    
    return render(request, 'dashboard.html', {
        'user_profile': profile,
        'invoices': invoices,
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'paid_invoices': paid_invoices,
        'total_revenue': total_revenue
    })

@login_required
def profile_setup(request):
    """User profile setup and update view"""
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'profile_setup.html', {
        'form': form, 
        'user_profile': profile,
        'is_new_profile': created
    })

@login_required
def document_choice(request):
    """Document type selection view"""
    return render(request, 'document_choice.html')

@login_required
def template_selection(request):
    """Template selection view"""
    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        return render(request, 'template_selection.html', {'document_type': document_type})
    return redirect('document_choice')

@login_required
def invoice_form(request):
    """Invoice creation form view"""
    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        template_id = request.POST.get('template_id')
        return render(request, 'invoice_form.html', {
            'document_type': document_type,
            'template_id': template_id
        })
    
    # If accessed via GET, redirect to document choice
    return redirect('document_choice')

@login_required
def preview(request):
    """Invoice preview view"""
    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        template_id = int(request.POST.get('template_id', 1))
        
        # Get template data
        template_data = TEMPLATES_DATA.get(template_id, TEMPLATES_DATA[1])
        
        # Extract form data
        invoice_data = {
            'invoice_number': request.POST.get('invoice_number'),
            'date': request.POST.get('date'),
            'client_name': request.POST.get('client_name'),
            'client_email': request.POST.get('client_email'),
            'client_phone': request.POST.get('client_phone'),
            'client_address': request.POST.get('client_address'),
            'notes': request.POST.get('notes'),
            'tax_rate': request.POST.get('tax_rate'),
            'subtotal': request.POST.get('subtotal', '0.00').replace('$', '').replace('₹', '').replace('€', '').replace('£', '').replace('¥', '').replace('A$', '').replace('C$', '').replace('CHF', '').replace('CN¥', ''),
            'tax_amount': request.POST.get('tax_amount', '0.00').replace('$', '').replace('₹', '').replace('€', '').replace('£', '').replace('¥', '').replace('A$', '').replace('C$', '').replace('CHF', '').replace('CN¥', ''),
            'total': request.POST.get('total', '0.00').replace('$', '').replace('₹', '').replace('€', '').replace('£', '').replace('¥', '').replace('A$', '').replace('C$', '').replace('CHF', '').replace('CN¥', ''),
            'currency': request.POST.get('currency', '₹'),  # Add currency
            'template': template_data  # Add template data
        }
        
        # Process items
        items = []
        descriptions = request.POST.getlist('item_description[]')
        quantities = request.POST.getlist('item_quantity[]')
        prices = request.POST.getlist('item_price[]')
        amounts = request.POST.getlist('item_amount[]')
        
        for i in range(len(descriptions)):
            if descriptions[i]:
                items.append({
                    'description': descriptions[i],
                    'quantity': quantities[i],
                    'price': prices[i],
                    'amount': amounts[i]
                })
        
        invoice_data['items'] = items
        
        user_profile = get_object_or_404(UserProfile, user=request.user)
        
        return render(request, 'preview.html', {
            'document_type': document_type,
            'template_id': template_id,
            'invoice_data': invoice_data,
            'user_profile': user_profile
        })
    
    return redirect('invoice_form')

@login_required
def save_invoice(request):
    """Save invoice to database"""
    if request.method == 'POST':
        try:
            # Create invoice
            invoice = Invoice(
                user=request.user,
                invoice_number=request.POST.get('invoice_number'),
                date=request.POST.get('date'),
                client_name=request.POST.get('client_name'),
                client_email=request.POST.get('client_email'),
                client_phone=request.POST.get('client_phone'),
                client_address=request.POST.get('client_address'),
                subtotal=request.POST.get('subtotal', '0').replace('$', '').replace('₹', '').replace('€', '').replace('£', '').replace('¥', '').replace('A$', '').replace('C$', '').replace('CHF', '').replace('CN¥', ''),
                tax_rate=request.POST.get('tax_rate', '0'),
                tax_amount=request.POST.get('tax_amount', '0').replace('$', '').replace('₹', '').replace('€', '').replace('£', '').replace('¥', '').replace('A$', '').replace('C$', '').replace('CHF', '').replace('CN¥', ''),
                total=request.POST.get('total', '0').replace('$', '').replace('₹', '').replace('€', '').replace('£', '').replace('¥', '').replace('A$', '').replace('C$', '').replace('CHF', '').replace('CN¥', ''),
                notes=request.POST.get('notes'),
                template_id=request.POST.get('template_id'),
                document_type=request.POST.get('document_type')
            )
            invoice.save()
            
            # Save invoice items
            descriptions = request.POST.getlist('item_description[]')
            quantities = request.POST.getlist('item_quantity[]')
            prices = request.POST.getlist('item_price[]')
            
            for i in range(len(descriptions)):
                if descriptions[i]:  # Only save if description exists
                    item = InvoiceItem(
                        invoice=invoice,
                        description=descriptions[i],
                        quantity=quantities[i],
                        price=prices[i],
                        amount=float(quantities[i]) * float(prices[i])
                    )
                    item.save()
            
            messages.success(request, f'{invoice.document_type.title()} saved successfully!')
            return redirect('dashboard')
        
        except Exception as e:
            messages.error(request, f'Error saving invoice: {str(e)}')
            return redirect('invoice_form')
    
    return redirect('invoice_form')

@login_required
def invoice_history(request):
    """View invoice history"""
    invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'invoice_history.html', {'invoices': invoices})

# Helper function to get template data
def get_template_data(template_id):
    """Get template data by ID"""
    return TEMPLATES_DATA.get(template_id, TEMPLATES_DATA[1])