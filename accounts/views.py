from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import IntegrityError

from .forms import SmartLearnLoginForm, SmartLearnRegisterForm, UserProfileForm


def login_view(request):
    """Handle user login with the SmartLearn split-screen design."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SmartLearnLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = SmartLearnLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """Handle user registration with role selection."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SmartLearnRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, f'Welcome to SmartLearn, {user.first_name}!')
                return redirect('dashboard')
            except IntegrityError:
                messages.error(request, 'An account with this email already exists. Please sign in instead.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = SmartLearnRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    """Log the user out and redirect to login."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    """Display and update user profile."""
    profile = request.user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update User model fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(
            instance=profile,
            initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        )

    context = {
        'form': form,
        'page_title': 'Profile',
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def settings_view(request):
    """User settings page."""
    context = {
        'page_title': 'Settings',
    }
    return render(request, 'accounts/settings.html', context)


def dashboard_router(request):
    """Route to the appropriate dashboard based on user role."""
    if not request.user.is_authenticated:
        return redirect('login')

    role = request.user.profile.role
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'faculty':
        return redirect('faculty_dashboard')
    else:
        return redirect('student_dashboard')
