from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django_messaging.models import DmMessage, DmUser
from django_messaging.controlers import time_to_duration

def index(request):
  if request.user.is_anonymous():
    return HttpResponse('')
  dm_users=DmUser.objects.all().select_related(depth=1).order_by('-last_activity')
  profile=dm_users.filter(user=request.user)[0]
  contacts_q=profile.contacts.all()
  contacts=[]
  for contact in contacts_q:
    contacts.append(contact)
  num_messages=profile.count_unreaded_messages()
  has_no_contacts=True
  contacts=[]
  for el in profile.contacts.all():
    contacts.append(el.username)
  if contacts<>[]:
    has_no_contacts=False
  #~ debug
  #msg=[]
  #msg.append('num msgs: '+str(num_messages))
  #msg.append('has msg: '+str(profile.has_message()))
  #msg.append('profile: '+str(profile))
  #msg.append('print contacs: '+str(profile.print_contacts()))
  #return render_to_response('debug.html',{'message':'<br />'.join(msg)},context_instance=RequestContext(request))
  #~ end debug
  user_contacts=[]
  for dm_user in dm_users:
    if dm_user.user<>request.user:
      if dm_user.user.username in contacts:
        dm_user.user.activity,is_offline=time_to_duration(dm_user.last_activity)
        dm_user.user.is_online=True
        if is_offline:
          dm_user.user.is_online=False
        dm_user.user.username=dm_user.user.username
        dm_user.user.dm_user_id=dm_user.id
        user_contacts.append(dm_user.user) 
  media_url=settings.MEDIA_URL
  return render_to_response('messaging/index.html',{'user_has_message':profile.has_message(),'user_num_messages':str(num_messages),'has_no_contacts':has_no_contacts,'user_contacts':user_contacts,'media_url':media_url},context_instance=RequestContext(request))
