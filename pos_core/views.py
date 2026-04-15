from django.shortcuts import render

def full_page(request, exception=None):
    return render(request, '404.html')
