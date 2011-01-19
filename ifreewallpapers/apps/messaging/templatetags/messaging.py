from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import SiteProfileNotAvailable
from django_messaging.models import DmUser

register = template.Library()

@register.tag
def messaging(parser,token):
  nodelist=parser.parse(('endmessaging',))
  parser.delete_first_token()
  return MessagingNode(nodelist)

class MessagingNode(template.Node):
  def __init__(self,nodelist):
    self.nodelist=nodelist

  def render(self,context):
    user=context['user']
    try:
      profile=DmUser.objects.all().select_related(depth='2')[0]
      profile.messages=profile.dmmessage_set.all()
      profile.num_messages=profile.messages.count()
    except SiteProfileNotAvailable:
      return 'no conf'
    except ObjectDoesNotExist:
      return 'no user'
    except Exception, e:
      return str(e)
    context['has_message']=False
    if profile.num_messages>0:
      context['has_message']=True
    context['has_contacts']=False
    contacts=profile.contacts.all()
    if list(contacts)<>[]:
      context['has_contacts']=True
    context['num_messages']=str(profile.num_messages)
    context['last_activity']=profile.last_activity 
    context['contacts']=contacts
    return ''

