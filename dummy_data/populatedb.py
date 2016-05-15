import os,sys,django

sys.path.append(os.path.dirname(os.path.abspath('.')))
os.environ["DJANGO_SETTINGS_MODULE"] = 'skill_huddle.settings'
django.setup()

from sh_app.models import SH_User,League,Suggestion,Huddle
from django.contrib.auth.models import User
from django_countries import countries
from localflavor.us.us_states import STATE_CHOICES
from django.utils import timezone
import random



def createUsers():

    random.seed()

    with open('adjectives.txt','r') as adjs,\
     open('nouns.txt','r') as nouns:

        list_adjs = adjs.readlines()
        list_nouns = nouns.readlines()

        for i in range(1,100):
            #create and save user object

            #random user name
            first_name = list_adjs[random.randint(0,len(list_adjs))].replace('\n','')
            last_name = list_nouns[random.randint(0,len(list_nouns))].replace('\n','')
            usrname = (first_name + '_' + last_name)[:30]

            usr = User(username = usrname,email = "gen123@gmail.com")
            usr.set_password("zxcvbnm,")
            usr.first_name = first_name
            usr.last_name = last_name
            sh = SH_User()
            try:
                usr.save()

                #create and save sh user
                sh.user = usr
                sh.first_name = first_name
                sh.last_name = last_name
                sh.save()
            except:
                mesage = "failed to create user:%s" % usrname
                print(mesage)


def createLeagues():
    random.seed()

    sh_users = SH_User.objects.all()
    list_countries   = list(map(lambda x: x[0],list(countries)))
    list_states      = list(map(lambda x: x[0],list(STATE_CHOICES)))
    string_book      = ''
    with open('aristotle.txt','r') as fi:
        string_book = fi.read()


    for i in range(1,10):
        new_league = League()
        with open('adjectives.txt','r') as adjs,open('nouns.txt','r') as nouns:
            list_adjs = adjs.readlines()
            list_nouns = nouns.readlines()
            name = "The %s %ss" % (list_adjs[random.randint(0,len(list_adjs)-1)].replace('\n',''), list_nouns[random.randint(0,len(list_nouns))].replace('\n',''))
            desc_start = random.randint(0,82824 - 300)
            description = string_book[desc_start : desc_start + 160]
            country = list_countries[random.randint(0,len(list_countries) -1)]
            if country == 'US':
                new_league.state = list_states[random.randint(0,len(list_states) -1)]
            city = list_nouns[random.randint(0,len(list_nouns))].replace('\n','')

            new_league.city = city
            new_league.name = name
            new_league.decription = description
            new_league.country = country

            new_league.head_official = sh_users[random.randint(0,len(sh_users) - 1)]
            try:
                new_league.save()
                new_league.officials.add(new_league.head_official)
                new_league.members.add(new_league.head_official)
            except:
                errormsg = 'Failed to create league: %s' % new_league.name
                print(errormsg)



def addLeagueMembers():
    random.seed()

    #add sh_users to the list
    for league in League.objects.all():
        usrs = list(SH_User.objects.all())
        usrs.remove(league.head_official)
        for i in range(0,25):
            new_member = usrs[random.randint(0,len(usrs) - 1)]
            usrs.remove(new_member)
            try:
                league.members.add(new_member)
            except:
                errormsg = "Failed to add member: %s" % new_member
                print(errormsg)


def addLeagueOfficials():
    random.seed()

    for league in League.objects.all():
        list_members = list(league.members.all())
        list_members.remove(league.head_official)

        for i in range(0,3):
            new_official = list_members[random.randint(0,len(list_members) -1)]
            list_members.remove(new_official)
            try:
                league.officials.add(new_official)
            except:
                errormsg = "Feiled to add official: %s" % new_official


def createSuggestions():
    random.seed()

    with open('adjectives.txt','r') as adjs,\
     open('nouns.txt','r') as nouns:

        list_adjs = adjs.readlines()
        list_nouns = nouns.readlines()

    string_book      = ''
    with open('aristotle.txt','r') as fi:
        string_book = fi.read()

    for league in League.objects.all():
        for i in range(0,10):
            tot_members = league.members.count()
            rand_user = league.members.all()[random.randint(0,tot_members -1)]
            name = list_adjs[random.randint(0,len(list_adjs)-1)].strip('\n') +\
            " " + list_nouns[random.randint(0,len(list_nouns)-1)].strip('\n') +\
            " " + list_nouns[random.randint(0,len(list_nouns)-1)]
            desc_start = random.randint(0,82824 - 300)
            description = string_book[desc_start : desc_start + 200]

            new_suggestion               = Suggestion()
            new_suggestion.name          = name
            new_suggestion.suggested_by  = rand_user
            new_suggestion.description   = description
            new_suggestion.voting_starts = timezone.now() -\
            timezone.timedelta(days=random.randint(0,10))
            new_suggestion.voting_ends   = new_suggestion.voting_starts +\
            timezone.timedelta(days=random.randint(1,10))

            try:
                new_suggestion.league = league
                new_suggestion.save()
                if new_suggestion.voting_ends < timezone.now():
                    random_int = random.randint(0, 2)
                    if random_int == 0:
                        for sh_user in league.members.all():
                            new_suggestion.upvotes.add(sh_user)
                            new_suggestion.is_accepted = True
                            new_suggestion.save()

            except:
                errormsg = "Failed to add Suggestion: %s" % new_suggestion
                print(errormsg)


def voteOnSuggestions():
    random.seed()

    for league in League.objects.all():
        for suggestion in league.suggestions.all():
            for member in league.members.all():
                votetype = random.randint(0,2)
                if votetype > 0:
                    if votetype == 1:
                        #upvote
                        try:
                            suggestion.upvotes.add(member)
                        except:
                            errormsg = "Failed to add upvoter %s" % member
                            print(errormsg)
                    else:
                        #downvote
                        try:
                            suggestion.downvotes.add(member)
                        except:
                            errormsg = "Failed to add downvoter %s" % member
                            print(errormsg)


def clearVotes():
    for league in League.objects.all():
        for suggestion in league.suggestions.all():
            try:
                suggestion.upvotes.clear()
            except:
                errormsg = "Failed to clear upvotes for %s" % suggestion
                print(errormsg)
            try:
                suggestion.downvotes.clear()
            except:
                errormsg = "Failed to clear downvotes for %s" % suggestion
                print(errormsg)


def createHuddles():
    random.seed()

    list_adjs     = []
    list_nouns    = []
    list_roadtype = ['Avenue','Road','Street','Drive']
    string_book = ''
    with open('adjectives.txt','r') as adjs,open('nouns.txt','r') as nouns,\
    open('aristotle.txt','r') as fi:
        list_adjs   = adjs.readlines()
        list_nouns  = nouns.readlines()
        string_book = fi.read()

    for league in League.objects.all():
        for i in range(0,10):
            name = list_adjs[random.randint(1,len(list_adjs))-1].strip('\n') + list_nouns[random.randint(1,len(list_nouns))-1].strip('\n') + "s"
            address = str(random.randint(1,1000)) +\
                      " " + list_nouns[random.randint(1,len(list_nouns))-1].strip('\n') +\
                      " " + list_roadtype[random.randint(1,len(list_roadtype))-1]
            desc_start  =  random.randint(0,82824 - 300)
            description =  string_book[desc_start : desc_start + 160]

            date        =  timezone.now() + timezone.timedelta(days=random.randint(-20,20))

            new_huddle             = Huddle()
            new_huddle.name        = name
            new_huddle.address     = address
            new_huddle.description = description
            new_huddle.league      = league
            new_huddle.date        = date
            list_officials = list(league.officials.all())

            try:
                new_huddle.save()
                for j in range(0,3):
                    expert = list_officials[random.randint(0,len(list_officials)-1)]
                    new_huddle.experts.add(expert)
                    list_officials.remove(expert)
            except:
                errormsg = "Failed to create: %s" % new_huddle


def clearHuddles():
    for league in League.objects.all():
        for huddle in league.huddles.all():
            huddle.delete()


def attendHuddles():
    random.seed()
    for league in League.objects.all():
        for huddle in league.huddles.all():
            for member in league.members.all():
                attendance = random.randint(0,10)
                if attendance ==0:
                    try:
                        huddle.attendants.add(member)
                    except:
                        errormsg = "Failed to add attendee: %s to huddle %s" % (member,huddle)
                        print(errormsg)

if __name__ == '__main__':
    createUsers()
    createLeagues()
    addLeagueMembers()
    addLeagueOfficials()
    createSuggestions()
    voteOnSuggestions()
    createHuddles()
    attendHuddles()
