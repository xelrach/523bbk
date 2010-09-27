import datetime
from bbk.models import *
from django_utils import *

def events(request):
    current = Event.objects.filter(end__gt=datetime.datetime.now())
    return render_to_response('events.html', {'events':current})

def event_create(request):
    event = Event()
    return render_to_response('event_edit.html', {'event':event})

def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render_to_response('event.html', {'event':event})

def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render_to_response('event_edit.html', {'event':event})
