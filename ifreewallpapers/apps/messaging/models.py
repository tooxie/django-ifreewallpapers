from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User

class DmUser(models.Model):
  user=models.ForeignKey(User,unique=True,related_name='dm_user')
  last_activity=models.DateTimeField(auto_now_add=True)
  contacts=models.ManyToManyField(User,related_name='dm_contact')

  def __unicode__(self):
    return 'profile> '+self.user.username

  def print_contacts(self):
    for contact in self.contacts.all():
      print str(contact.id)+' - '+contact.username
    return

  def get_messages(self):
    return self.dmmessage_set.all()

  def get_message(self,message_id):
    try:
      return self.get_messages().filter(id=message_id,to_user=self)[0]
    except ObjectDoesNotExist:
      #~ this guy is trying to read other user's pm
      return None

  def get_first_unreaded_message(self):
    try:
      return self.get_messages().order_by('-date').filter(to_user=self,readed=False)[0]
    except ObjectDoesNotExist:
      return None

  def print_messages(self):
    msgs=self.get_messages()
    readed_msgs=0
    unreaded_msgs=0
    for msg in msgs:
      readed='' 
      if msg.readed:
        readed=' - readed'
        readed_msgs=readed_msgs+1
      else:
        unreaded_msgs=unreaded_msgs+1
      print 'id: '+str(msg.id)+' - '+str(msg)+readed
    if list(msgs)==[]:
      print 'No messages'
    else:
      print str(readed_msgs)+' readed messages'
      print str(unreaded_msgs)+' unreaded messages'
    return

  def delete_message(self,message_id):
    try:
      msg=self.get_messages().filter(id=message_id)
    except ObjectDoesNotExists:
      return False
    print 'Deleting message '+str(msg)
    msg.delete()
    return True

  def delete_all_messages(self):
    msgs=self.get_messages()
    i=0
    for msg in msgs:
      self.delete_message(msg.id)
      i=i+1
    print str(i)+' messages deleted'
    return 

  def send_message(self,to_user,message):
    msg=DmMessage(from_user=self,to_user=to_user,message=message)
    msg.save()
    return True

  def has_message(self):
    return self.count_unreaded_messages()>0

  def count_messages(self):
    return self.get_messages().count()

  def count_unreaded_messages(self):
    readed=0
    for message in self.get_messages():
      if message.readed==False:
        readed=readed+1
    return readed

  class Admin:
    pass

class DmMessage(models.Model):
  to_user=models.ForeignKey(DmUser)
  from_user=models.ForeignKey(DmUser,related_name='from_user')
  date=models.DateTimeField(auto_now_add=True)
  message=models.CharField(max_length=255)
  readed=models.BooleanField(default=False)

  def __unicode__(self):
    return self.from_user.user.username+' ('+str(self.from_user.id)+') -> '+self.to_user.user.username+'('+str(self.to_user.id)+')'

  class Admin:
    pass
