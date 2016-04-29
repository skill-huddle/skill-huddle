from django import forms
from django.forms import Textarea
from sh_app.models import User, League

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ('name', 'description', 'country', 'city', 'state', 'is_private', 'head_official')
        widgets = {
            'description': Textarea
        }
