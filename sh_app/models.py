from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

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
	country = models.CharField(max_length=10)
	city = models.CharField(max_length=20)
	state = models.CharField(max_length=20,blank=True)
	date_created = models.TimeField(default=timezone.now)#required
	is_private = models.BooleanField(default=False)

	head_official = models.ForeignKey(SH_User,related_name='HOfficial_of')#required what to do on delete
	officials = models.ManyToManyField(SH_User,related_name='Official_of')#
	members = models.ManyToManyField(SH_User,related_name='LM_of')

	def __str__(self):
		return self.name


class Huddle(models.Model):
	"""
	No implicit fields
	"""
	name = models.CharField(max_length=50)
	address = models.CharField(max_length=100)
	time = models.TimeField(blank=True)
	description = models.CharField(max_length=260)

	league = models.ForeignKey(League,on_delete=models.CASCADE,related_name='huddles')
	experts = models.ManyToManyField(SH_User,related_name='expert_of')
	attendants = models.ManyToManyField(SH_User,related_name='attending')

	def __str__(self):
		return self.name


class Suggestion(models.Model):
	"""
	No implicit fields
	"""
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=260)
	isAccepted = models.BooleanField(default=False)
	votingstarts = models.TimeField()
	votingends = models.TimeField()

	suggestedby = models.ForeignKey(SH_User,related_name='suggestions')
	league = models.ForeignKey(League,related_name='suggestions')
	upvotes = models.ManyToManyField(SH_User,related_name='upvoted_on',blank=True)
	downvotes = models.ManyToManyField(SH_User,related_name='downvoted_on',blank=True)

	def __str__(self):
		return self.name 