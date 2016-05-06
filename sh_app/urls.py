from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^restricted/$', views.restricted, name='restricted'),
    url(r'^leagues/$', views.leagues, name='leagues'),
    url(r'^leagues/create/$', views.create_league, name='create_league'),
    url(r'^leagues/(?P<league_id>[0-9]+)/$', views.league_detail, name='league_detail'),
    url(r'^leagues/(?P<league_id>[0-9]+)/create_suggestion/$', views.create_suggestion, name='create_suggestion'),
]

