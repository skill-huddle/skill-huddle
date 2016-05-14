import django
from sh_app.models import SH_User
from django.contrib.auth.models import User
import random

def createUsers():

	random.seed()

	with open('adjectives.txt','r') as adjs,\
	 open('nouns.txt','r') as nouns:

		list_adjs = adjs.readlines()
		list_nouns = nouns.readlines()

		for i in range(1,10):
			#create and save user object

			#random user name
			usrname = list_nouns[random.randint(0,len(list_nouns))].replace('\n','') + \
			 '_' + list_adjs[random.randint(0,len(list_adjs))].replace('\n','')

			usr = User(name = usrname,email = "gen123@gmail.com")
			usr.set_password("zxcvbnm,")
			try:
				usr.save()

				#create and save sh user
				sh.user = usr 
				sh.save()
			except:
				mesage = "failed to create user:%s" % username
				print(mesage) 
