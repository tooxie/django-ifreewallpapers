from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response 
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django_messaging.models import DmMessage,DmUser
from django_messaging.views import index

@login_required
def send_pm(request,dm_user_id):
  contact_username=DmUser.objects.get(id=dm_user_id).user.username
  return render_to_response('messaging/send_pm.html',{'contact_id':dm_user_id,'contact_username':contact_username})

@login_required
def post_pm(request,dm_user_id):
  profile=request.user.get_profile()
  to_user=DmUser.objects.get(id=dm_user_id)
  profile.send_message(to_user=to_user,message=request.GET['pm'])
  return index(request)

@login_required
def read_pm(request,message_id=None,first=None):
  if first:
    message=request.user.get_profile().get_first_unreaded_message()
  else:
    message=request.user.get_profile().get_message(message_id)
  if not message:
    return HttpResponse('Impossible de lire le message')  
  #~ flag the message as readed
  if not message.readed:
    message.readed=True
    #~ save data
    message.save()
  message.from_user_username=message.from_user.user.username
  return render_to_response('messaging/read_pm.html',{'message':message})

@login_required
def read_first_pm(request):
  return read_pm(request,first=True)

@login_required
def load_num_msgs(request):
  num_messages=request.user.get_profile().count_unreaded_messages()
  has_message=False
  if num_messages>0:
    has_message=True
  return render_to_response('messaging/num_messages.html',{'has_message':has_message,'num_messages':num_messages,'media_url':settings.MEDIA_URL})

@login_required
def load_msgs_list(request):
  profile=request.user.get_profile()
  has_messages=False
  messages_q=profile.get_messages().order_by('-date')
  if len(list(messages_q))>0:
    has_messages=True
  messages=[]
  for message in messages_q:
    message.from_username=message.from_user.user.username
    messages.append(message)
  return render_to_response('messaging/messages_list.html',{'messages':messages,'has_messages':has_messages,'media_url':settings.MEDIA_URL})

@login_required
def delete_message(request,message_id):
  profile=request.user.get_profile() 
  profile.delete_message(int(message_id)) 
  return HttpResponseRedirect('/messaging/load_msgs_list/')
