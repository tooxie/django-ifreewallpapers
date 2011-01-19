from django.conf.urls.defaults import *
from models import *

urlpatterns = patterns('faq.views',
    url(r'^$', 'index', name='faq_index'),
)
