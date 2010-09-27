from django.conf.urls.defaults import *

urlpatterns = patterns('bbk.views',
    (r'^volunteer_signup/$', 'volunteer_signup'),
    (r'^admin/$', 'admin'),
    (r'^volunteer/$', 'volunteer'),
)
#URLs for events
urlpatterns += patterns('bbk.views',
    (r'^event/$', 'events'),
    (r'^event/create/$', 'event_create'),
    (r'^event/(?P<event_id>\d+)/$', 'event_details'),
    (r'^event/(?P<event_id>\d+)/edit/$', 'event_edit'),
)
#Serve static files
urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static'}),
)
