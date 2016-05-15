from django import forms
from django.forms import Textarea
from sh_app.models import User, SH_User, League, Suggestion, Huddle

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class SH_UserForm(forms.ModelForm):
    class Meta:
        model = SH_User
        fields = ('first_name', 'last_name')

class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ('name', 'description', 'country', 'city', 'state')
        help_texts = {
            'description': 'Maximum {} characters'.format(League._meta.get_field('description').max_length)
        }
        widgets = {
            'description': Textarea
        }

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ('name', 'description', 'voting_ends')
        help_texts = {
            'description': 'Maximum {} characters'.format(Suggestion._meta.get_field('description').max_length)
        }
        widgets = {
            'description': Textarea,
        }

class HuddleForm(forms.ModelForm):
    class Meta:
        model = Huddle
        fields = ('name', 'address', 'date', 'description')
        help_texts = {
            'description': 'Maximum {} characters'.format(Huddle._meta.get_field('description').max_length)
        }
        widgets = {
            'description': Textarea,
        }
