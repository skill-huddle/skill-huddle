from django.shortcuts import render


def home(request):
    """
    View to serve the home page
    """
    return render(request, "search/index.html")


