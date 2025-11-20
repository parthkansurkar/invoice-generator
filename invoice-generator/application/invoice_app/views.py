# invoice_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from .forms import CustomUserCreationForm, UserProfileForm, PasswordResetForm, SetNewPasswordForm
from .models import UserProfile, Invoice, InvoiceItem, PasswordResetOTP

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
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
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
                    
            except IntegrityError:
                messages.error(request, 'This email is already registered. Please use a different email.')
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {str(e)}')
        else:
            # Form is invalid, show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def custom_login(request):
    """Custom login view to handle authentication"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Check if user has a complete profile
            try:
                profile = UserProfile.objects.get(user=user)
                if not profile.company_name or not profile.phone:
                    messages.info(request, 'Please complete your business profile.')
                    return redirect('profile_setup')
            except UserProfile.DoesNotExist:
                messages.info(request, 'Please complete your business profile setup.')
                return redirect('profile_setup')
                
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    
    return render(request, 'login.html')

def forgot_password(request):
    """Forgot password - Step 1: Enter email to get OTP"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                # Use filter().first() to handle multiple users
                user = User.objects.filter(email=email).first()
                if not user:
                    messages.error(request, 'No account found with this email address.')
                    return render(request, 'forgot_password.html', {'form': form})
                
                # Generate OTP
                otp_obj = PasswordResetOTP.generate_otp(user)
                
                # Print OTP to console
                print(f"\n{'='*50}")
                print(f"PASSWORD RESET OTP for {email}")
                print(f"OTP: {otp_obj.otp}")
                print(f"Valid for 10 minutes")
                print(f"{'='*50}\n")
                
                messages.success(request, f'OTP has been sent. Check console for OTP.')
                request.session['reset_email'] = email
                request.session['user_id'] = user.id
                return redirect('verify_otp')
                    
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = PasswordResetForm()
    
    return render(request, 'forgot_password.html', {'form': form})

def verify_otp(request):
    """Forgot password - Step 2: Verify OTP"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    email = request.session.get('reset_email')
    user_id = request.session.get('user_id')
    
    if not email or not user_id:
        messages.error(request, 'Please start the password reset process again.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        try:
            user = User.objects.filter(id=user_id).first()
            if not user:
                messages.error(request, 'User not found. Please start over.')
                return redirect('forgot_password')
            
            otp_obj = PasswordResetOTP.objects.filter(
                user=user, 
                otp=otp, 
                is_used=False
            ).first()
            
            if otp_obj and otp_obj.is_valid():
                otp_obj.mark_used()
                request.session['otp_verified'] = True
                messages.success(request, 'OTP verified successfully. You can now set your new password.')
                return redirect('set_new_password')
            else:
                messages.error(request, 'Invalid or expired OTP. Please try again.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('forgot_password')
    
    return render(request, 'verify_otp.html', {'email': email})

def set_new_password(request):
    """Forgot password - Step 3: Set new password"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if not request.session.get('otp_verified'):
        messages.error(request, 'Please verify OTP first.')
        return redirect('forgot_password')
    
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please start over.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(id=user_id)
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                
                # Clear session data
                request.session.pop('reset_email', None)
                request.session.pop('otp_verified', None)
                request.session.pop('user_id', None)
                
                messages.success(request, 'Password reset successfully! You can now login with your new password.')
                return redirect('login')
                
            except User.DoesNotExist:
                messages.error(request, 'User not found. Please start over.')
                return redirect('forgot_password')
    else:
        form = SetNewPasswordForm()
    
    return render(request, 'set_new_password.html', {'form': form})

def custom_logout(request):
    """Custom logout view to handle logout properly"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('landing')
    else:
        # If accessed via GET, show confirmation page
        return render(request, 'logout_confirmation.html')

@login_required
def dashboard(request):
    """Dashboard view for authenticated users"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create a default profile if it doesn't exist
        profile = UserProfile.objects.create(
            user=request.user,
            company_name="Your Company",
            phone="Not provided",
            address="Not provided", 
            pan_number="Not provided"
        )
        messages.info(request, 'Please complete your business profile setup.')
        return redirect('profile_setup')
    
    # If profile is incomplete, redirect to setup
    if not profile.company_name or profile.company_name == "Your Company" or not profile.phone or profile.phone == "Not provided":
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
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error saving profile: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'profile_setup.html', {
        'form': form, 
        'user_profile': profile
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
        # Pass the templates data to the template
        templates = TEMPLATES_DATA.items()
        return render(request, 'template_selection.html', {
            'document_type': document_type,
            'templates': templates
        })
    return redirect('document_choice')

@login_required
def invoice_form(request):
    """Invoice creation form view"""
    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        template_id = request.POST.get('template_id')
        
        # Get template data for the selected template
        template_data = TEMPLATES_DATA.get(int(template_id), TEMPLATES_DATA[1])
        
        return render(request, 'invoice_form.html', {
            'document_type': document_type,
            'template_id': template_id,
            'template_data': template_data  # Pass template data to form
        })
    
    # If accessed via GET, redirect to document choice
    return redirect('document_choice')

@login_required
def preview(request):
    """Invoice preview view"""
    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        template_id = int(request.POST.get('template_id', 1))
        
        # Get template data for the selected template
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
            'currency': request.POST.get('currency', '₹'),
            'template': template_data  # Use the selected template data
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
                template_id=request.POST.get('template_id', 1),  # Save the selected template_id
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