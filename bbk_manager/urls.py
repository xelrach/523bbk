from django.conf.urls.defaults import *
import os

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

urlpatterns = patterns('bbk.views',
    (r'^$', 'home'),
    (r'^admin/$', 'admin'),
    (r'^application/$', 'application'),
    (r'^read_application/(?P<volunteer_id>\d+)/$', 'read_application'),
    (r'^login/$', 'login'),
    (r'^logout/$', 'logout'),
    (r'^reset/$', 'password_reset'),
    (r'^pending/$', 'pending'),
    (r'^signed_up/$', 'signed_up'),
    (r'^profile/$', 'profile'),
    (r'^volunteer_signup/$', 'volunteer_signup'),
    (r'^volunteer/(?P<volunteer_id>\d+)/$', 'volunteer'),
    (r'^volunteers/$', 'volunteers'),
    (r'^volunteers/(?P<status>\w+)/$', 'volunteers_xml'),
)
#URLs for events
urlpatterns += patterns('bbk.views',
    (r'^events/$', 'events'),
    (r'^events/ical/$', 'events_ical'),
    (r'^events/admin/$', 'events_admin'),
    (r'^events/user/$', 'events_user'),
    (r'^event/admin/(?P<event_id>\d+)/$', 'event_admin_details'),
    (r'^event/create/$', 'event_create'),
    (r'^event/(?P<event_id>\d+)/$', 'event_details'),
    (r'^event/(?P<event_id>\d+)/edit/$', 'event_edit'),
)
#Serve static files
urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(SITE_ROOT, 'static')}),
)
