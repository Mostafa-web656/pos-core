# core/middleware.py
from django.utils import timezone
from django.shortcuts import redirect

# core/middleware.py
class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)  # <-- بدل request.user مباشر
        if user and user.is_authenticated:
            # نفذ الكود اللي محتاجه
            pass
        response = self.get_response(request)
        return response
