from django.shortcuts import render

"""
View to serve the home page
"""
def home(request):
    return render(request, "skill_huddle/index.html")