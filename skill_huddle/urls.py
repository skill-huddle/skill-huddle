from django.conf.urls import include, url
from django.contrib import admin
from sh_app import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'skill_huddle.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include('sh_app.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
