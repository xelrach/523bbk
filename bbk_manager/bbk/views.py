import datetime
import re
from django import forms
from bbk.models import *
from django_utils import *

def admin(request):
    user = check_login(request)
    return render_to_response("admin.html", {'user':user})

def application(request):
    user = check_login(request)
    n_references = 3
    if not user:
        return HttpResponseRedirect(reverse('bbk.views.volunteer_signup'))
    if user.status=="active" or user.status=="admin":
        return HttpResponseRedirect(reverse('bbk.views.events'))

    application = Application(user=user)
    try:
        application = Application.objects.get(user=user)
    except:
        pass
    qs_refs = Reference.objects.filter(application=application).select_related('address','phone')
    references = [Reference(id=-(i+1)) for i in xrange(max(n_references,len(qs_refs)))]
    for i, ref in enumerate(qs_refs):
        references[i] = ref
    if request.method=="POST":
        application.former_names = request.POST.get('former_names','')
        application.experience = request.POST.get('experience','')
        application.skills = request.POST.get('skills','')
        application.involvement = request.POST.get('involvement','')
        application.save()

        ref_map = {}
        for name, value in request.POST.iteritems():
            match = re.match('reference_(\w+)\[(-?\d+)\]', name)
            if not match:
                continue
            id = int(match.group(2))
            if not ref_map.get(id):
                try:
                    ref = Reference.objects.get(id=id)
                except:
                    ref = Reference()
                    ref.address = Address()
                    ref.phone = Phone()
                ref_map[id] = ref
            ref = ref_map[id]
            if match.group(1) == 'name':
                ref.name = value
                continue
            if match.group(1) == 'email':
                ref.email = value
                continue
            if match.group(1) == 'phone':
                ref.phone.number = value
                continue
            if match.group(1) == 'address_line1':
                ref.address.line1 = value
                continue
            if match.group(1) == 'address_line2':
                ref.address.line2 = value
                continue
            if match.group(1) == 'address_city':
                ref.address.city = value
                continue
            if match.group(1) == 'address_state':
                ref.address.state = value
                continue
            if match.group(1) == 'address_zip':
                ref.address.zip = value
                continue
        for ref in ref_map.values():
            ref.application = application
            ref.address.save()
            ref.phone.save()
            ref.address = ref.address
            ref.phone = ref.phone
            ref.save()

        if request.POST.get('s') == ('submit'):
            return HttpResponseRedirect(reverse('bbk.views.pending'))
        else:
            return HttpResponseSeeOther(reverse('bbk.views.application'))
    user.application = application
    return render_to_response("application.html", {'user':user,'references':references})

def check_login(request):
    try:
        return User.objects.get(id=request.session['auth_id'])
    except:
        return None

def events(request):
    current_event_list = Event.objects.filter(end__gt=datetime.datetime.now())
    return render_to_response('events.html', {'current_event_list':current_event_list})

def event_create(request):
    event = Event()
    if request.method=="POST":
        try:	    
            event.title = request.POST['title']
    	    event.description = request.POST['description']
            event.start = request.POST['start']
            event.end = request.POST['end']    
            event.save()
            return HttpResponseRedirect(reverse('bbk.views.events'))
	except Exception as e:
	    print e
	    pass
    return render_to_response('event_create.html', {'event':event})

def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = User.objects.get(id=request.session['auth_id'])
    if request.method=="POST":
        event.volunteers.add(user)
        event.save()
        return HttpResponseRedirect(reverse('bbk.views.events'))
    return render_to_response('event.html', {'event':event})

def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method=="POST":
        try:	    
            event.title = request.POST['title']
    	    event.description = request.POST['description']
            event.start = request.POST['start']
            event.end = request.POST['end']    
            event.save()
            return HttpResponseRedirect(reverse('bbk.views.events'))
	except Exception as e:
	    print e
	    pass
    return render_to_response('event_edit.html', {'event':event})

def events_admin(request):
    current_event_list = Event.objects.filter(end__gt=datetime.datetime.now())
    return render_to_response('events_admin.html', {'current_event_list':current_event_list})

def event_admin_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event_volunteers = event.volunteers.all()
    length = len(event_volunteers)
    return render_to_response('event_admin.html', {'event':event, 'event_volunteers':event_volunteers, 'length':length})

def login(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.POST['email'].lower())
            user.check_password(request.POST['password'])
            request.session.set_expiry(None)
            request.session['auth_id'] = user.id
            if user.status=="applying" or user.status=="pending":
                return HttpResponseRedirect(reverse('bbk.views.application'))
            if user.status=="active":
                return HttpResponseRedirect(reverse('bbk.views.events'))
            if user.status=="admin":
                return HttpResponseRedirect(reverse('bbk.views.admin'))
        except Exception as e:
            return render_to_response('login.html', {'message':"Login Failed"})
    return render_to_response('login.html')

def logout(request):
    request.session.flush()
    pass

def pending(request):
    return render_to_response('pending.html')

def volunteer(request,volunteer_id):
    volunteer = get_object_or_404(User, id=volunteer_id)
    return render_to_response('volunteer.html', {'volunteer':volunteer})

def volunteer_signup(request):
    user = User()
    user.phone = ''
    if request.POST and len(request.POST)>0:
        logout(request)
        try:
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            if request.POST['pwd1']<>request.POST['pwd2']:
                raise Exception
            user.set_password(request.POST['pwd1'])
            phone = Phone()
            phone.number = request.POST['phone']
            user.save()
            phone.save()
            user.phones.add(phone)
            if not is_valid_email(user.email):
              raise forms.ValidationError('%s is not a valid e-mail address.' % email)
            user.save()
            request.session.set_expiry(None)
            request.session['auth_id'] = user.id
            return HttpResponseRedirect(reverse('bbk.views.application'))
        except Exception as e:
            pass
        pass
    return render_to_response('volunteer_signup.html', {'user':user})

def volunteers(request):
    vols = User.objects.all().order_by('last_name')
    return render_to_response("volunteers.html", {"volunteers":vols})

def volunteers_xml(request, status):
    vols = User.objects
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
