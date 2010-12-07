import datetime
import dateutil.parser
import re
from django import forms
from bbk.models import *
from django_utils import *
from django.core.mail import EmailMultiAlternatives

def admin(request):
    user = check_login(request)
    if not user or user.status != "admin":
        return HttpResponseRedirect(reverse('bbk.views.events'))
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
        application.why = request.POST.get('why','')
        application.how = request.POST.get('how','')
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

        if request.POST.get('s') == ('Submit'):
            user.status = "pending"
            user.save()
            application.save()
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
    user = check_login(request)
    current_event_list = Event.objects.filter(end__gt=datetime.datetime.now())
    url_ical = request.build_absolute_uri(reverse('bbk.views.events_ical'))
    return render_to_response('events.html', {'current_event_list':current_event_list,'user':user,'url_ical':url_ical})

def event_create(request):
    user = check_login(request)
    event = Event()
    if request.method=="POST":
        try:
            event.title = request.POST['title']
    	    event.description = request.POST['description']
            event.start = dateutil.parser.parse(request.POST['start'])
            event.end = dateutil.parser.parse(request.POST['end'])
            event.save()
            return HttpResponseRedirect(reverse('bbk.views.events'))
	except Exception as e:
	    print e
	    pass
    if event.start is None:
        event.start = datetime.datetime.now()
    if event.end is None:
        event.end = datetime.datetime.now()
    return render_to_response('event_create.html', {'event':event,'user':user})

def event_details(request, event_id):
    user = check_login(request)
    event = get_object_or_404(Event, id=event_id)
    user = User.objects.get(id=request.session['auth_id'])
    if request.method=="POST":
        event.volunteers.add(user)
        event.save()
        return HttpResponseRedirect(reverse('bbk.views.signed_up'))
    return render_to_response('event.html', {'event':event, 'user':user})

def signed_up(request):
    user = check_login(request)
    return render_to_response('signed_up.html',{'user':user})

def event_edit(request, event_id):
    user = check_login(request)
    event = get_object_or_404(Event, id=event_id)
    if request.method=="POST":
        try:	    
            event.title = request.POST['title']
    	    event.description = request.POST['description']
            event.start = dateutil.parser.parse(request.POST['start'])
            event.end = dateutil.parser.parse(request.POST['end'])
            event.save()
            return HttpResponseRedirect(reverse('bbk.views.events'))
	except Exception as e:
	    print e
	    pass
    return render_to_response('event_edit.html', {'event':event, 'user':user})

def events_ical(request):
    current_event_list = Event.objects.filter(end__gt=datetime.datetime.now())
    print current_event_list
    response = render_to_response('events.ics', {'events':current_event_list}, "text/calendar")
    response['Content-Disposition'] = 'attachment; filename="BounceBack Kids.ics"'
    return response

def events_admin(request):
    user = check_login(request)
    current_event_list = Event.objects.filter(end__gt=datetime.datetime.now())
    return render_to_response('events_admin.html', {'current_event_list':current_event_list, 'user':user})

def events_user(request):
    user = check_login(request)
    user_id = user.id
    user_events = Event.objects.filter(volunteers=user_id)
    return render_to_response('events_user.html',{'user_events':user_events,'user':user})

def event_admin_details(request, event_id):
    user = check_login(request)
    event = get_object_or_404(Event, id=event_id)
    event_volunteers = event.volunteers.all()
    length = len(event_volunteers)
    return render_to_response('event_admin.html', {'event':event,'user':user, 'event_volunteers':event_volunteers, 'length':length})

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
    perform_logout(request)
    return HttpResponseRedirect(reverse('bbk.views.events'))

def perform_logout(request):
    request.session.flush()
    pass

def pending(request):
    user = check_login(request)
    return render_to_response('pending.html', {'user':user})

def send_acception_email(volunteer):
    acception_message_base = "You've been accpeted as a volunteer for BounceBack Kids! Please visit "
    events_url = reverse('bbk.views.events')
    acception_message_txt = acception_message_base + events_url
    acception_message_html = acception_message_base + '<a href="' + events_url + '">' + events_url + "</a>"
    subject, from_email, to = "BounceBack Kids Application", "admin@bouncebackkids.org", [volunteer.email]

    msg = EmailMultiAlternatives(subject, acception_message_txt, from_email, to)
    msg.attach_alternative(acception_message_html, "text/html")
    msg.send()

def volunteer(request,volunteer_id):
    user = check_login(request)
    if not user or user.status != "admin":
        return HttpResponseRedirect(reverse('bbk.views.events'))
    volunteer = get_object_or_404(User, id=volunteer_id)

    message = ""
    try:
        checklist = Checklist.objects.get(user=volunteer.id)
    except Exception as e:
        checklist = Checklist(user=volunteer)
    if request.method=="POST":
        if request.POST.get("submit","") != "Save":
            return HttpResponseRedirect(reverse("bbk.views.volunteers"))

        if "first_name" in request.POST:
            volunteer.first_name = request.POST['first_name']
        if "last_name" in request.POST:
            volunteer.last_name = request.POST['last_name']
        if "title" in request.POST:
            volunteer.title = request.POST['title']
        if "email" in request.POST:
            volunteer.email = request.POST['email']
        if "status" in request.POST:
            if volunteer.status == "pending" and request.POST['status']=="active":
                send_acception_email(volunteer)
            volunteer.status = request.POST['status']
            pass
        volunteer.save()
        post_checklist = request.POST.getlist('user_checklist')
        try:
            if "Confidential Form" in post_checklist:   
                checklist.confidential_form = True
            else:
                checklist.confidential_form = False
            if "Background Check" in post_checklist:   
                checklist.background_check = True
            else:
                checklist.background_check = False
            if "Vaccines" in post_checklist:   
                checklist.vaccines = True
            else:
                checklist.vaccines = False
            if "References" in post_checklist:
                checklist.references = True
            else:
                checklist.references = False
        except Exception as e:
            print e
        volunteer.save()
        checklist.save()
        message = "User Changes Saved"
    return render_to_response('volunteer.html', {'volunteer':volunteer,'user':user,'message':message, 'checklist':checklist})

def volunteer_signup(request):
    user = User()
    user.phone = ''
    if request.POST and len(request.POST)>0:
        perform_logout(request)
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
            # validation syntax below doesn't seem to be working.
            #if not is_valid_email(user.email):
            # raise forms.ValidationError('%s is not a valid e-mail address.' % email)
            user.status = "applying"
            user.save()
            request.session.set_expiry(None)
            request.session['auth_id'] = user.id
            return HttpResponseRedirect(reverse('bbk.views.application'))
        except Exception as e:
            pass
        pass
    return render_to_response('volunteer_signup.html', {'user':user})

def volunteers(request):
    user = check_login(request)
    if not user or user.status != "admin":
        return HttpResponseRedirect(reverse('bbk.views.events'))
    return render_to_response("volunteers.html", {"user":user})

def volunteers_xml(request, status):
    user = check_login(request)
    if not user or user.status != "admin":
        raise Http404
    vols = User.objects
    if status == "all":
        vols = vols.filter(status__in=["active","admin","coordinator","pending"])
    elif status == "active":
        vols = vols.filter(status__in=["active","admin","coordinator"])
    elif status == "pending":
        vols = vols.filter(status="pending")
    else:
        raise Http404

    vols = vols.order_by('last_name')
    return render_to_response("volunteers.xml", {"volunteers":vols}, "text/xml")
