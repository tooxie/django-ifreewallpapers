from datetime import datetime
#from django.http import HttpResponse
from django_messaging.models import DmUser

class DjangoMessagingMiddleware(object):
  def process_request(self,request):
    msg=''
    if request.user.is_authenticated():
      dm_user,created=DmUser.objects.get_or_create(user=request.user)
      #~ update user last activity
      dm_user.last_activity=datetime.now()
      dm_user.save()
    return None
       
