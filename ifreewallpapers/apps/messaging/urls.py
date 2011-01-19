from django.conf.urls.defaults import *

urlpatterns = patterns('django_messaging.views',
     (r'^$', 'index'),
     (r'^read_first_pm/$', 'messages.read_first_pm'),
     (r'^read_pm/(?P<message_id>\w+)/$', 'messages.read_pm'),
     (r'^load_num_msgs/$', 'messages.load_num_msgs'),
     (r'^load_msgs_list/$', 'messages.load_msgs_list'),
     (r'^delete_message/(?P<message_id>\w+)/$', 'messages.delete_message'),
     (r'^contacts/$', 'contacts.contacts'),
     (r'^contacts/(?P<contact_id>\w+)/add/$', 'contacts.add_contact'),
     (r'^contacts/(?P<contact_id>\w+)/remove/$', 'contacts.remove_contact'),
     (r'^send_pm/(?P<dm_user_id>\w+)/$', 'messages.send_pm'),
     (r'^post_pm/(?P<dm_user_id>\w+)/$', 'messages.post_pm'),
)
