"""
User Authentication Views
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from .models import CustomUser


def home(request):
    """Homepage view"""
    return render(request, 'users/home.html')


def register(request):
    """
    User registration view
    - Creates new user account
    - Generates RSA keys encrypted with password
    - Logs user in automatically
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create user (password is auto-hashed by Django)
            user = form.save()
            
            # Generate RSA keys for encryption
            password = form.cleaned_data.get('password1')
            user.generate_rsa_keys(password)
            
            # Log the user in
            login(request, user)
            
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('users:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """
    User login view
    - Authenticates user
    - Decrypts RSA private key and stores in session
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authenticate user
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Decrypt RSA private key with password
                private_key = user.decrypt_private_key(password)
                
                if private_key:
                    # Store decrypted key in session (encrypted by Django)
                    request.session['private_key'] = private_key.decode('utf-8')
                    
                    # Log user in
                    login(request, user)
                    
                    messages.success(request, f'Welcome back, {user.username}!')
                    return redirect('users:dashboard')
                else:
                    messages.error(request, 'Failed to decrypt encryption keys.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    User logout view
    - Clears session (including decrypted private key)
    """
    # Clear private key from session
    if 'private_key' in request.session:
        del request.session['private_key']
    
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('users:home')


@login_required
def dashboard(request):
    """User dashboard view"""
    return render(request, 'users/dashboard.html')


@login_required
def profile(request):
    """User profile view"""
    return render(request, 'users/profile.html')
