from django.shortcuts import render


def index(request):
    '''
    Serve view for home page
    '''
    return render(request, "index.html")


def about(request):
    '''
    Serve view for about page
    '''
    return render(request, "about.html")
