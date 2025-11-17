"""
Middleware to prevent caching of authenticated pages and prevent back button access after logout
"""
from django.utils.cache import add_never_cache_headers


class NoCacheMiddleware:
    """
    Middleware to prevent caching of authenticated pages
    This prevents users from accessing cached pages after logout
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add no-cache headers for authenticated pages
        if request.user.is_authenticated:
            add_never_cache_headers(response)
            # Additional cache control headers
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response


