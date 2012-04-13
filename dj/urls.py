# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf.urls.defaults import patterns, url, include

from django.conf.urls.defaults import patterns, url
from django.views.generic import ListView, DetailView
from hp.models import *


urlpatterns = patterns('',
                       url(r'^single', 'hp.views.single'),
                       url(r'^postcode', 'hp.views.postcode'),
                       url(r'^price', 'hp.views.price'),
                       url(r'^hi', 'hp.views.hi'),
                       url(r'^', 'hp.views.index'),

  #url(r'^admin/', include(admin.site.urls)),
  #url(r'^', include(admin.site.urls))
)
