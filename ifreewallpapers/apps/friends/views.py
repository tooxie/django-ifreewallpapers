from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from friends.models import Contact

@login_required
def friend_user(request, username):
        user = User.objects.get(username=username)
        friends, created = Contact.objects.get_or_create(user=request.user)
        friends.users.add(user)
        return HttpResponseRedirect(request.GET.get('next', '/'))
