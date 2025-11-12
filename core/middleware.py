# auth/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class ProfileSetupMiddleware:
    """
    Middleware to ensure users complete their profile setup
    before accessing other pages
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # URLs that should be accessible without profile completion
        allowed_urls = [
            reverse('login'),
            reverse('register'),
            reverse('profile_setup'),
            reverse('logout'),
            '/static/',
            '/media/',
        ]
        
        # Check if user is authenticated and profile is not completed
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                if not profile.profile_completed:
                    # Allow access to profile setup and allowed URLs
                    if not any(request.path.startswith(url) for url in allowed_urls):
                        return redirect('profile_setup')
            except:
                # If profile doesn't exist, create it
                pass
        
        response = self.get_response(request)
        return response