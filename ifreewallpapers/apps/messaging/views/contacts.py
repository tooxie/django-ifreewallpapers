from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required
def contacts(request):
  users=list(User.objects.all())
  users.remove(request.user)
  profile=request.user.get_profile()
  contacts=profile.contacts.all()
  return render_to_response('messaging/contacts.html',{'users':users,'contacts':contacts})

@login_required
def add_contact(request,contact_id):
  profile=request.user.get_profile()
  contact=User.objects.get(id=contact_id)
  profile.contacts.add(contact)
  profile.save()
  return contacts(request)

@login_required
def remove_contact(request,contact_id):
  profile=request.user.get_profile()
  contact_user=User.objects.get(id=contact_id)
  profile.contacts.remove(contact_user)
  return contacts(request)
