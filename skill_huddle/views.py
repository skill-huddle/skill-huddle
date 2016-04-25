from django.shortcuts import render


def home(request):
    """
    View to serve the home page
    """
    return render(request, "skill_huddle/index.html")