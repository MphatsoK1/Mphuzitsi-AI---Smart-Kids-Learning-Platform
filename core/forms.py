from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import *

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter your username or email'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter your password'
        })
    )

    def clean_username_or_email(self):
        username_or_email = self.cleaned_data.get('username_or_email')
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                return user.username
            except User.DoesNotExist:
                raise ValidationError("No account found with this email address.")
        return username_or_email

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise ValidationError("Invalid username/email or password.")
        return cleaned_data

class RegisterForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': True})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'required': True})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")
        return password2

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        return user
    

# core/forms.py
from django import forms
from .models import UserProfile

class ProfileSetupForm(forms.ModelForm):
    # Define choices for preset avatars (matching the template's avatar IDs)
    AVATAR_CHOICES = [
        ('58509039_9439767', 'avatar1'),
        ('58509042_9439833', 'avatar2'),
        ('58509054_9441186', 'avatar3'),
        ('58509040_9434650', 'avatar4'),
    ]

    selected_avatar = forms.ChoiceField(
        choices=AVATAR_CHOICES,
        required=True,  # Require selection to avoid validation errors
        widget=forms.HiddenInput  # Matches the template's hidden input
    )

    class Meta:
        model = UserProfile
        fields = ['selected_avatar']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:
            instance.user = self.user
        instance.profile_completed = True
        if commit:
            instance.save()
        return instance