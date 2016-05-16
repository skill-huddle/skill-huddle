from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

from django_countries.fields import CountryField
from localflavor.us.us_states import STATE_CHOICES
from localflavor.us.models import USStateField

class SH_User(models.Model):
    """
    Implicit fields:
        HOfficial_of
        Official_of
        LM_of
        expert_of
        attending
        suggestions
        upvoted_on
        downvoted_on
    """
    # Fixes problem where Django displays S h_user and S h_users for SH_User model
    class Meta:
        verbose_name = "SH_User"
        verbose_name_plural = "SH_Users"

    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=30, null=True, blank=False)
    last_name = models.CharField(max_length=30, null=True, blank=False)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.user.username

class League(models.Model):
    """
    Implicit fields:
        huddles
        suggestions
    """
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=260)
    country = CountryField()
    city = models.CharField(max_length=20)
    state = USStateField(blank=True, null=True, choices=STATE_CHOICES)
    date_created = models.DateTimeField(default=timezone.now)
    is_private = models.BooleanField(default=False)

    head_official = models.ForeignKey(SH_User, related_name='HOfficial_of', on_delete=models.CASCADE)
    officials = models.ManyToManyField(SH_User, related_name='Official_of')
    members = models.ManyToManyField(SH_User, related_name='LM_of')

    def __str__(self):
        return self.name

    def is_member(self, sh_user):
        return sh_user in self.members.all()

    def is_official(self, sh_user):
        return sh_user in self.officials.all()

    def is_head_official(self, sh_user):
        return sh_user == self.head_official



class Huddle(models.Model):
    """
    No implicit fields
    """
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=260)

    league = models.ForeignKey(League, related_name='huddles', on_delete=models.CASCADE,)
    experts = models.ManyToManyField(SH_User, related_name='expert_of')
    attendants = models.ManyToManyField(SH_User, related_name='attending')

    def __str__(self):
        return self.name

    def is_expert(self, sh_user):
        return sh_user in self.experts.all()

    def is_attending(self, sh_user):
        return sh_user in self.attendants.all()


def validate_vote_time(date):
        if date < timezone.now():
            raise ValidationError("Vote must start and end in future.")

def set_default_vote_end_time():
    return timezone.now() + timezone.timedelta(days=7)

class Suggestion(models.Model):
    """
    No implicit fields
    """
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=260)
    is_accepted = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    voting_starts = models.DateTimeField(default=timezone.now)
    voting_ends = models.DateTimeField(default=set_default_vote_end_time, validators=[validate_vote_time])

    suggested_by = models.ForeignKey(SH_User, related_name='suggestions', on_delete=models.CASCADE)
    league = models.ForeignKey(League, related_name='suggestions', on_delete=models.CASCADE)
    upvotes = models.ManyToManyField(SH_User, related_name='upvoted_on', blank=True)
    downvotes = models.ManyToManyField(SH_User, related_name='downvoted_on', blank=True)

    def __str__(self):
        return self.name

    def is_suggested_by(self, sh_user):
        return sh_user == self.suggested_by

    def is_upvoted_by(self, sh_user):
        return sh_user in self.upvotes.all()

    def is_downvoted_by(self, sh_user):
        return sh_user in self.downvotes.all()

    def is_voted_on_by(self, sh_user):
        return self.is_downvoted_by(sh_user) or self.is_upvoted_by(sh_user)

    def tally_votes(self):
        num_upvotes = self.upvotes.count()
        num_downvotes = self.downvotes.count()
        tally = num_upvotes - num_downvotes
        return tally

    def is_voting_ended(self):
        return self.voting_ends < timezone.now()

