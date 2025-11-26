from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from datetime import date
from django.core.exceptions import ValidationError

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter to handle date_of_birth for social logins"""
    
    def is_open_for_signup(self, request, socialaccount):
        """Allow social signups"""
        return True
    
    def save_user(self, request, sociallogin, form=None):
        """Save user and create profile with date_of_birth if provided"""
        user = super().save_user(request, sociallogin, form)
        
        # Get date_of_birth from form if available
        if form and hasattr(form, 'cleaned_data') and 'date_of_birth' in form.cleaned_data:
            date_of_birth = form.cleaned_data['date_of_birth']
            if date_of_birth:
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.date_of_birth = date_of_birth
                profile.save()
        
        return user
    
    def populate_user(self, request, sociallogin, data):
        """Populate user data from social account"""
        user = super().populate_user(request, sociallogin, data)
        return user


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom adapter to handle date_of_birth for regular signups"""
    
    def save_user(self, request, user, form, commit=True):
        """Save user and profile with date_of_birth"""
        user = super().save_user(request, user, form, commit)
        
        # Get date_of_birth from form if available
        if hasattr(form, 'cleaned_data') and 'date_of_birth' in form.cleaned_data:
            date_of_birth = form.cleaned_data['date_of_birth']
            if date_of_birth:
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.date_of_birth = date_of_birth
                if commit:
                    profile.save()
        
        return user

