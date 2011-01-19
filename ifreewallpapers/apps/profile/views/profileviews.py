# coding=UTF-8
from profile.models import Profile
# from profile import settings as _settings

from utils.decorators import render_response
to_response = render_response('profile/')

# from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
# from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404

"""
@to_response
def overview(request, ):
    return 'profile.html'
"""

@to_response
def public(request, slug):
    profile = Profile.objects.get(slug=slug)
    return 'public.html', {'profile': profile}
