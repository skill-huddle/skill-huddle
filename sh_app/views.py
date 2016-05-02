from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from sh_app.forms import UserForm, SH_UserForm, LeagueForm, SuggestionForm
from sh_app.models import League


def index(request):
    """
    Serve view for home page
    """
    return render(request, "index.html")


def about(request):
    """
    Serve view for about page
    """
    return render(request, "about.html")

def register(request):

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and SH_User.
        user_form = UserForm(data=request.POST)
        sh_user_form = SH_UserForm(data=request.POST);

        # If the two forms are valid...
        if user_form.is_valid() and sh_user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)

            # Now sort out the SH_User instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            sh_user = sh_user_form.save(commit=False)
            sh_user.user = user
            user.first_name = sh_user.first_name
            user.last_name = sh_user.last_name

            # Now we save the User and SH_User model instance.
            user.save()
            sh_user.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print(user_form.errors, sh_user_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        sh_user_form = SH_UserForm()

    # Render the template depending on the context.
    return render(request,
                  'register.html',
                  {'user_form': user_form, 'sh_user_form': sh_user_form, 'registered': registered} )

def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
        # because the request.POST.get('<variable>') returns None, if the value does not exist,
        # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your SH account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'login.html', {})

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect(reverse('index'))

@login_required
def create_league(request):
    if request.method == 'POST':
        # User has submitted the create league form
        league_form = LeagueForm(data=request.POST)
        if league_form.is_valid():
            # Add SH_User associated with current user to head_official, officials, league_members and save to database
            sh_user = request.user.sh_user
            # Get league model from form, but do not save to database
            league = league_form.save(commit=False)
            # Set foreign key relation
            league.head_official = sh_user
            # Cannot add many-to-many relations until the object already exists in database
            league.save()
            # Now that object exists, can set the many-to-many relations.
            league.officials.add(sh_user)
            league.members.add(sh_user)
            league.save()

            return HttpResponseRedirect(reverse('index'))
        else:
            print(league_form.errors)

    else:
        # GET request, serve empty form
        league_form = LeagueForm()

    return render(request, 'create_league.html', {'league_form': league_form})

@login_required
def create_suggestion(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    sh_user = request.user.sh_user
    if league.is_member(sh_user):
        if request.method == 'POST':
            # User has submitted the create suggestion form
            suggestion_form = SuggestionForm(data=request.POST)
            if suggestion_form.is_valid():
                # Set suggested_by and league foreign key relation
                # Get suggestion model from form, but do not save to database
                suggestion = suggestion_form.save(commit=False)
                # Set foreign key relations
                suggestion.suggested_by = sh_user
                suggestion.league = league
                suggestion.save()

                return HttpResponseRedirect(reverse('index'))
            else:
                print(suggestion_form.errors)

        else:
            # GET request, serve empty SuggestionForm
            suggestion_form = SuggestionForm()

    else:
        return HttpResponse("You must be a league member of league {} to view this page".format(league.name))

    return render(request, 'create_suggestion.html', {'suggestion_form': suggestion_form, 'league': league})

def leagues(request):
    list_of_leagues = League.objects.all()
    if list_of_leagues:
        return render(request, 'leagues.html', {'list_of_leagues': list_of_leagues})

def league_detail(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    return render(request, 'league_detail.html', {'league': league})
