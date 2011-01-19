from django_messaging.models import DmUser, DmMessage
from django.contrib.auth.models import User

#~ ========== init data ===========
#~ get data
users=User.objects.all()
dm_users=DmUser.objects.all()
#dm_messages=DmMessage.objects.all()
try:
  #~ configure here the users you want to test with
  username1='syntax_error'
  username2='testman'
  #~ get user data
  user1=users.filter(username=username1)[0]
  user2=users.filter(username=username2)[0]
  #~ get messaging data stored in the user profile class (defined in AUTH_PROFILE_MODULE in settings.py)
  user1.profile=user1.get_profile()
  user2.profile=user2.get_profile()
except:
  pass

#~ ============= notes =============
#~ It is recomanded to run create_all_profiles() to initiate user profiles before starting to use the module. Use check_profiles() to see what user profiles are not yet created. If a user do not have a profile it is automaticly created via the middleware when the authenticated user loads a page when he is logged in.

#~ ============= users =============
def list_dm_users():
  for dm_user in dm_users:
    print 'User '+dm_user.user.username+' ('+str(dm_user.user.id)+') - Dm user: '+str(dm_user.id)
  return

def list_users():
  for user in users:
    print user.username
  return

def check_all_users():
  missing=[]
  dm_users_ids=[]
  for dm in dm_users:
    dm_users_ids.append(dm.user.id)
  for user in users:
    if user.id in dm_users_ids:
      print user.username+' has dm_user'
    else:
      missing.append(user.username)
  print '###### Users that do not have a dm_user: #####'
  print ' - '.join(missing)
  return

def create_all_dm_users():
  dm_users_ids=[]
  for dm in dm_users:
    dm_users_ids.append(dm.user.id)
  for user in users:
    if user.id in dm_users_ids:
      print user.username+' already has dm_user'
    else:
      dm_user=DmUser(user=user)
      dm_user.save()
      print 'dm_user created for '+user.username
  return

