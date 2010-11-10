from django.conf.urls.defaults import *
import os

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

urlpatterns = patterns('bbk.views',
    (r'^admin/$', 'admin'),
    (r'^application/$', 'application'),
    (r'^login/$', 'login'),
    (r'^pending/$', 'pending'),
    (r'^volunteer_signup/$', 'volunteer_signup'),
    (r'^volunteer/$', 'volunteer'),
    (r'^volunteers/$', 'volunteers'),
    (r'^volunteers/(?P<status>\w+)/$', 'volunteers_xml'),
)
#URLs for events
urlpatterns += patterns('bbk.views',
    (r'^event/$', 'events'),
    (r'^events/$', 'events'),
    (r'^event/create/$', 'event_create'),
    (r'^event/(?P<event_id>\d+)/$', 'event_details'),
    (r'^event/(?P<event_id>\d+)/edit/$', 'event_edit'),
)
#Serve static files
urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(SITE_ROOT, 'static')}),
)
