# coding=UTF-8
from django.utils.translation import ugettext_lazy as _
from decorators import render_response
from models import *
to_response = render_response('faq/')

@to_response
def index(request):
    return 'index.html'

