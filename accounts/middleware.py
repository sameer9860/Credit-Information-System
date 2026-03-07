from django.utils.cache import add_never_cache_headers

class NoCacheMiddleware:
    """
    Middleware that adds headers to prevent the browser from caching responses.
    This is important for security, so that when a user logs out and clicks 'back',
    they don't see the previous authenticated page content from the cache.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add headers to prevent caching for all responses
        # Alternatively, you could check if the user is authenticated, 
        # but applying it generally is safer for a credit system.
        add_never_cache_headers(response)
        
        return response
