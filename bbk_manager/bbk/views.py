import datetime
from django import forms
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

def potential_volunteers(request):
    users = User.objects.all()
    return render_to_response('volunteers_potential.html', {'volunteers': users})

def volunteer_signup(request):
    user = User()
    user.phone = ''
    if request.POST and len(request.POST)>0:
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        try:
#            if not is_valid_email(user.email):
#                raise forms.ValidationError('%s is not a valid e-mail address.' % email)
            user.save()
            print "Success!"
            return render_to_response('volunteer_signedup.html', {'user':user})
        except Exception as e:
            print e
            pass
        pass
    print "New/Failed Sign Up"
    return render_to_response('volunteer_signup.html', {'user':user})

def volunteers(request):
    vols = User.objects.all().order_by('last_name')
    return render_to_response("volunteers.html", {"volunteers":vols})

def volunteers_xml(request, status):
    print "volunteers_xml"
    vols = User.objects
    print status
    print dir(status)
    if status == "all":
        vols = vols.all()
    elif status == "active":
        vols = vols.filter(status="active")
    elif status == "pending":
        vols = vols.filter(Q(status="pending") | Q(status="started"))
    else:
        raise Http404

    vols = vols.order_by('last_name')
    return render_to_response("volunteers.xml", {"volunteers":vols}, "text/xml")
