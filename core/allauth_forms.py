from allauth.account.forms import SignupForm as AllauthSignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from datetime import date
from django.core.exceptions import ValidationError

class CustomSignupForm(AllauthSignupForm):
    """Custom signup form that includes date_of_birth"""
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'required': True
        }),
        required=True,
        help_text="We use this to provide age-appropriate games for you!"
    )
    
    def clean_date_of_birth(self):
        """Validate date of birth"""
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            
            # Validate minimum age (e.g., 3 years)
            if age < 3:
                raise ValidationError("You must be at least 3 years old to use this platform.")
            
            # Validate maximum age (e.g., 100 years for reasonable limit)
            if age > 100:
                raise ValidationError("Please enter a valid date of birth.")
        
        return date_of_birth
    
    def save(self, request):
        """Save user and profile with date_of_birth"""
        user = super().save(request)
        
        # Save date_of_birth to profile
        if hasattr(user, 'profile'):
            user.profile.date_of_birth = self.cleaned_data['date_of_birth']
            user.profile.save()
        else:
            from .models import UserProfile
            UserProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth']
            )
        
        return user


class CustomSocialSignupForm(SocialSignupForm):
    """Custom social signup form that includes date_of_birth"""
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'required': True
        }),
        required=True,
        help_text="We use this to provide age-appropriate games for you!"
    )
    
    def clean_date_of_birth(self):
        """Validate date of birth"""
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            
            # Validate minimum age (e.g., 3 years)
            if age < 3:
                raise ValidationError("You must be at least 3 years old to use this platform.")
            
            # Validate maximum age (e.g., 100 years for reasonable limit)
            if age > 100:
                raise ValidationError("Please enter a valid date of birth.")
        
        return date_of_birth
    
    def save(self, request):
        """Save user and profile with date_of_birth"""
        user = super().save(request)
        
        # Save date_of_birth to profile
        if hasattr(user, 'profile'):
            user.profile.date_of_birth = self.cleaned_data['date_of_birth']
            user.profile.save()
        else:
            from .models import UserProfile
            UserProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth']
            )
        
        return user

