from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from sh_app.forms import UserForm, SH_UserForm, LeagueForm, SuggestionForm, HuddleForm
from sh_app.models import League, Suggestion, SH_User, Huddle


def index(request):
    """
    Serve view for home page
    """
    return render(request, "index.html")

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
                return render(request, 'redirect.html', {
                    'title': 'Account Disabled',
                    'heading': 'Banned',
                    'content': 'Your account has been disabled. Contact an administrator.',
                    'url_arg': 'index',
                    'url_text': 'Back to homepage'
                })

        else:
            # Bad login details were provided. So we can't log the user in.
            return render(request, 'redirect.html', {
                'title': 'Invalid Login',
                'heading': 'Incorrect Login',
                'content': 'Invalid login details for: {0}'.format(username),
                'url_arg': 'login',
                'url_text': 'Back to login'
            })
    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'login.html', {})

@login_required
def profile(request, sh_user_id):
    sh_user = get_object_or_404(SH_User, pk=sh_user_id)
    official_list = sh_user.Official_of.all()
    member_list = set(sh_user.LM_of.all()) - set(official_list)

    return render(request, 'profile.html', {'sh_user': sh_user, 'member_list': member_list, 'official_list': official_list})

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
                suggestion.voting_starts = timezone.now()
                suggestion.save()

                return HttpResponseRedirect(reverse('league_detail', args=[league_id]))
            else:
                print(suggestion_form.errors)

        else:
            # GET request, serve empty SuggestionForm
            suggestion_form = SuggestionForm()

    else:
        return render(request, 'redirect_with_arg.html', {
            'title': 'Restricted',
            'heading': 'Page Unavailable',
            'content': 'You must be a member of {} to create a suggestion'.format(league.name),
            'url_arg': 'league_detail',
            'url_arg_id': league_id,
            'url_text': 'Back to {}'.format(league)
            })

    return render(request, 'create_suggestion.html', {'suggestion_form': suggestion_form, 'league': league})

@login_required
def suggestion_detail(request, suggestion_id):
    suggestion = get_object_or_404(Suggestion, pk=suggestion_id)
    sh_user = request.user.sh_user
    if not suggestion.league.is_member(sh_user):
        return render(request, 'redirect_with_arg.html', {
            'title': 'Restricted',
            'heading': 'Page Unavailable',
            'content': 'You must be a member of {} to view suggestion details'.format(suggestion.league.name),
            'url_arg': 'league_detail',
            'url_arg_id': suggestion.league.id,
            'url_text': 'Back to {}'.format(suggestion.league)
            })

    if request.method == 'POST':
        for key in request.POST.keys():
            if "upvote" in key:
                suggestion.downvotes.remove(sh_user)
                suggestion.upvotes.add(sh_user)
                suggestion.save()
            elif "downvote" in key:
                suggestion.upvotes.remove(sh_user)
                suggestion.downvotes.add(sh_user)
                suggestion.save()

    context = {
        'suggestion': suggestion,
        'already_voted': suggestion.is_voted_on_by(sh_user),
        'already_upvoted': suggestion.is_upvoted_by(sh_user),
    }

    return render(request, 'suggestion_detail.html', context)

def leagues(request):
    list_of_leagues = League.objects.all()
    return render(request, 'leagues.html', {'list_of_leagues': list_of_leagues})

def league_detail(request, league_id):
    league = get_object_or_404(League, pk=league_id)

    if request.user.is_authenticated():
        sh_user = request.user.sh_user
        if request.method == "POST":
            # Clicked join or leave league
            if "join" in request.POST.keys():
                league.members.add(sh_user)
            else:
                # Clicked leave
                for suggestion in league.suggestions.all():
                    if suggestion.is_suggested_by(sh_user):
                        suggestion.delete()
                league.members.remove(sh_user)
                if league.is_official(sh_user):
                    league.officials.remove(sh_user)
                if league.is_head_official(sh_user):
                    league.delete()
                    return HttpResponseRedirect(reverse('index'))

            league.save()
            return render(request, 'league_detail.html',
                          {'league': league,
                           'is_head_official': league.is_head_official(sh_user),
                           'is_official': league.is_official(sh_user),
                           'is_member': league.is_member(sh_user)})
        else:
            # Get request
            return render(request, 'league_detail.html',
                        {'league': league,
                         'is_head_official': league.is_head_official(sh_user),
                         'is_official': league.is_official(sh_user),
                         'is_member': league.is_member(sh_user)})
    else:
        # User not logged in
        return render(request, 'league_detail.html',
                      {'league': league,
                       'is_head_official': False,
                       'is_official': False,
                       'is_member': False})

@login_required
def manage_league_membership(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    sh_user = request.user.sh_user

    if league.is_head_official(sh_user):
        if request.method == "POST":
            # Promoted or demoted the sh_user
            for key, value in request.POST.items():
                if "demote" in key:
                    target_user = key.split('_')[1]
                    league.officials.remove(target_user)
                    league.save()
                elif "promote" in key:
                    target_user = key.split('_')[1]
                    league.officials.add(target_user)
                    league.save()

        list_of_officials = set(league.officials.all()) - set([sh_user])
        list_of_members = set(league.members.all()) - list_of_officials - set([sh_user])
        return render(request, 'manage_league_membership.html',
                      {'league': league,
                       'list_of_members': list_of_members,
                       'list_of_officials': list_of_officials,
                       'head_official': sh_user})
    else:
        # User is not a head official
        return render(request, 'redirect_with_arg.html', {
            'title': 'Restricted',
            'heading': 'Page Unavailable',
            'content': 'You must be a head official of {} to manage league members'.format(league.name),
            'url_arg': 'league_detail',
            'url_arg_id': league_id,
            'url_text': 'Back to {}'.format(league)
            })

@login_required
def manage_league_suggestions(request, league_id):
    league = get_object_or_404(League, pk=league_id)

    # Redirect if not official
    if not league.is_official(request.user.sh_user):
        return render(request, 'redirect_with_arg.html', {
            'title': 'Restricted',
            'heading': 'Page Unavailable',
            'content': 'You must be an official of {} to manage league suggestions'.format(league.name),
            'url_arg': 'league_detail',
            'url_arg_id': league.id,
            'url_text': 'Back to {}'.format(league)
            })

    # Update all suggestion approval statuses for the league
    suggestions_vote_ended_not_approved = league.suggestions.filter(voting_ends__lte=timezone.now()).filter(is_accepted=False)
    for suggestion in suggestions_vote_ended_not_approved:
        if suggestion.tally_votes() > 3:
            suggestion.is_accepted = True
            suggestion.save()

    list_approved_suggestions = league.suggestions.filter(is_accepted=True).filter(is_archived=False)
    return render(request, 'manage_league_suggestions.html',
                  {'league': league,
                   'list_of_approved_suggestions': list_approved_suggestions})

@login_required
def create_huddle(request, suggestion_id):
    suggestion = get_object_or_404(Suggestion, pk=suggestion_id)

    # Redirect if not official
    if not suggestion.league.is_official(request.user.sh_user):
        return render(request, 'redirect_with_arg.html', {
            'title': 'Restricted',
            'heading': 'Page Unavailable',
            'content': 'You must be an official of {} to create a huddle'.format(suggestion.league.name),
            'url_arg': 'league_detail',
            'url_arg_id': suggestion.league.id,
            'url_text': 'Back to {}'.format(suggestion.league)
            })

    if request.method == 'POST':
        huddle_form = HuddleForm(data=request.POST)
        if huddle_form.is_valid():
            huddle = huddle_form.save(commit=False)
            huddle.league = suggestion.league
            huddle.save()
            huddle.experts.add(request.user.sh_user)
            huddle.attendants.add(request.user.sh_user)
            huddle.save()
            suggestion.is_archived = True
            suggestion.save()

            return HttpResponseRedirect(reverse('league_detail', args=[suggestion.league.id]))
    else:
        huddle = Huddle()
        huddle.name = suggestion.name
        huddle.description = suggestion.description
        huddle.league = suggestion.league
        huddle_form = HuddleForm(instance=huddle)

    return render(
        request,
        'create_huddle.html',
        {'huddle_form': huddle_form, 'suggestion_id': suggestion_id})

@login_required
def huddle_detail(request, huddle_id):
    huddle = get_object_or_404(Huddle, pk=huddle_id)
    sh_user = request.user.sh_user
    if not huddle.league.is_member(sh_user):
        return render(request, 'redirect_with_arg.html', {
            'title': 'Restricted',
            'heading': 'Page Unavailable',
            'content': 'You must be a member of {} to view huddle details'.format(huddle.league.name),
            'url_arg': 'league_detail',
            'url_arg_id': huddle.league.id,
            'url_text': 'Back to {}'.format(huddle.league)
            })

    if request.method == "POST":
        # Clicked attend or attend as expert
        for key in request.POST.keys():
            if "not_attending_as_expert" in key:
                huddle.experts.remove(sh_user)
                huddle.attendants.remove(sh_user)
                huddle.save()
            elif "not_attending_as_member" in key:
                huddle.attendants.remove(sh_user)
                huddle.save()
            elif "attending_as_expert" in key:
                huddle.experts.add(sh_user)
                huddle.attendants.add(sh_user)
                huddle.save()
            elif "attending_as_member" in key:
                huddle.attendants.add(sh_user)
                huddle.save()

    huddle_attendants = huddle.attendants.all()
    list_of_attendants = set(huddle_attendants) - set(huddle.experts.all())
    not_attending = sh_user not in huddle_attendants
    context = {
        'huddle': huddle,
        'not_attending': not_attending,
        'attending_as_expert': huddle.is_expert(sh_user),
        'is_official': huddle.league.is_official(sh_user),
        'list_of_attendants': list_of_attendants,
    }
    print(context)
    return render(request, 'huddle_detail.html', context)


