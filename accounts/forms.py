from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import UserProfile


class SmartLearnLoginForm(AuthenticationForm):
    """Custom login form matching the SmartLearn design."""

    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control sl-input',
            'placeholder': 'you@example.com',
            'id': 'email',
            'autocomplete': 'email',
        }),
        label='Email',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control sl-input',
            'placeholder': 'Enter your password',
            'id': 'password',
            'autocomplete': 'current-password',
        }),
        label='Password',
    )


class SmartLearnRegisterForm(UserCreationForm):
    """Custom registration form with role selection."""

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control sl-input',
            'placeholder': 'First name',
            'id': 'first_name',
        }),
        label='First Name',
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control sl-input',
            'placeholder': 'Last name',
            'id': 'last_name',
        }),
        label='Last Name',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control sl-input',
            'placeholder': 'you@example.com',
            'id': 'email',
            'autocomplete': 'email',
        }),
        label='Email',
    )
    role = forms.ChoiceField(
        choices=[('student', 'Student'), ('faculty', 'Faculty')],
        widget=forms.Select(attrs={
            'class': 'form-select sl-input',
            'id': 'role',
        }),
        label='I am a',
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control sl-input',
            'placeholder': 'Min. 8 characters',
            'id': 'password1',
            'autocomplete': 'new-password',
        }),
        label='Password',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control sl-input',
            'placeholder': 'Confirm your password',
            'id': 'password2',
            'autocomplete': 'new-password',
        }),
        label='Confirm Password',
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check both email and username (email is used as username)
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Update the auto-created profile with the selected role
            user.profile.role = self.cleaned_data['role']
            user.profile.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control sl-input',
            'id': 'first_name',
        }),
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control sl-input',
            'id': 'last_name',
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control sl-input',
            'id': 'email',
        }),
    )

    class Meta:
        model = UserProfile
        fields = ['bio', 'phone', 'department', 'date_of_birth', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control sl-input', 'rows': 3, 'id': 'bio'}),
            'phone': forms.TextInput(attrs={'class': 'form-control sl-input', 'id': 'phone'}),
            'department': forms.TextInput(attrs={'class': 'form-control sl-input', 'id': 'department'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control sl-input', 'type': 'date', 'id': 'dob'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control sl-input', 'id': 'avatar'}),
        }
