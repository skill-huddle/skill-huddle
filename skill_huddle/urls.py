from django.conf.urls import include, url
from django.contrib import admin

from skill_huddle import views


urlpatterns = [
    # Examples:
    # url(r'^$', 'skill_huddle.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.home, name='home'),
    url(r'^admin/', include(admin.site.urls)),
]
