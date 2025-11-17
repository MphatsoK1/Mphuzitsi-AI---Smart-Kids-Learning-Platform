from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import *

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

    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True
        })
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
        # Create the main user
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )

        # Update the profile created by the signal with DOB
        # The signal automatically creates a profile, so we update it instead of creating a new one
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.date_of_birth = self.cleaned_data['date_of_birth']
        profile.save()

        return user

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
        required=True,
        widget=forms.HiddenInput
    )
    
    # Add date_of_birth field if profile doesn't have it
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': False  # Not required if already set
        }),
        required=False,
        help_text="We use this to provide age-appropriate games for you!"
    )

    class Meta:
        model = UserProfile
        fields = ['selected_avatar']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        # If profile doesn't have date_of_birth, make it required
        if instance and not instance.date_of_birth:
            self.fields['date_of_birth'].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:
            instance.user = self.user

        # Set preset avatar to match attribute name in model
        instance.preset_avatar = self.cleaned_data['selected_avatar']
        
        # Save date_of_birth if provided and not already set
        if 'date_of_birth' in self.cleaned_data and self.cleaned_data['date_of_birth']:
            if not instance.date_of_birth:
                instance.date_of_birth = self.cleaned_data['date_of_birth']

        instance.profile_completed = True

        if commit:
            instance.save()
        return instance


class ChangePasswordForm(forms.Form):
    """Form for changing user password"""
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter your current password'
        }),
        required=True
    )
    
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter your new password'
        }),
        required=True,
        min_length=8
    )
    
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirm your new password'
        }),
        required=True
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("Your current password is incorrect.")
        return old_password
    
    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if new_password1:
            try:
                validate_password(new_password1, self.user)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return new_password1
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError("The two password fields didn't match.")
        
        return cleaned_data
    
    def save(self):
        """Update the user's password"""
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


class EditProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter your username'
        }),
        required=True,
        max_length=150
    )
    
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-input w-full focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter your email'
        }),
        required=False
    )
    
    # Avatar choices
    AVATAR_CHOICES = [
        ('58509039_9439767', 'avatar1'),
        ('58509042_9439833', 'avatar2'),
        ('58509054_9441186', 'avatar3'),
        ('58509040_9434650', 'avatar4'),
    ]
    
    selected_avatar = forms.ChoiceField(
        choices=AVATAR_CHOICES,
        required=False,
        widget=forms.HiddenInput
    )
    
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={
            'class': 'form-input w-full focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        }),
        required=False,
        help_text="We use this to provide age-appropriate games for you!"
    )
    
    class Meta:
        model = UserProfile
        fields = ['selected_avatar', 'date_of_birth']
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill username and email from user model
        if instance:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Check if username is already taken by another user
            if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
                raise ValidationError("This username is already taken. Please choose another.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
                raise ValidationError("This email is already taken. Please choose another.")
        return email
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Update user's username and email
        if 'username' in self.cleaned_data:
            self.user.username = self.cleaned_data['username']
        if 'email' in self.cleaned_data:
            self.user.email = self.cleaned_data['email']
        self.user.save()
        
        # Update profile
        if 'selected_avatar' in self.cleaned_data and self.cleaned_data['selected_avatar']:
            instance.preset_avatar = self.cleaned_data['selected_avatar']
        
        if 'date_of_birth' in self.cleaned_data and self.cleaned_data['date_of_birth']:
            instance.date_of_birth = self.cleaned_data['date_of_birth']
        
        if commit:
            instance.save()
        return instance
