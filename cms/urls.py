from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from cms.models import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('cms.views',
   url(r'^$', 'show',{'slug':"/%s"%settings.HOME_SLUG}, name='cms.home'),            # contenido definido en home slug
   url(r'^%s/$'%settings.HOME_SLUG, RedirectView.as_view(url='/', permanent=False)), # redirect 
   url(r'(?P<slug>.*)/$', 'show',name='cms.show'),

)