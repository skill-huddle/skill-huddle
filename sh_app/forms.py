from django import forms
from sh_app.models import User, SH_User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class SH_UserForm(forms.ModelForm):
    class Meta:
        model = SH_User
        fields = ('first_name','last_name')
