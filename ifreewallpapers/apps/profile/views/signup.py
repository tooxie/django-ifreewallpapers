# coding=UTF-8
from profile.models import Registration
from profile.forms import SignupForm, InputKeyForm, SetPasswordForm

from utils import next
from utils.decorators import render_response

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404

to_response = render_response('profile/')

@to_response
def signup(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    signup_form = SignupForm()
    if request.method == 'POST':
        post = request.POST.copy()
        signup_form = SignupForm(post)
        if signup_form.is_valid():
            start_registration(request)
            return HttpResponseRedirect(reverse('signup-email') + '?next=' + next(request))
    return 'signup.html', {'signup_form': signup_form, 'next': next(request)}

def start_registration(request):
    from profile.profileutils import keygen, send_registration_key

    post = request.POST.copy()
    user = User(
        username=post.get('email'),
        email=post.get('email'),
        first_name=post.get('first_name'),
        last_name=post.get('last_name'),
        is_active=False)
    password = keygen(user)[:8]
    user.set_password(password)
    user.save()

    registration = Registration(user=user, key=keygen(user))
    registration.save()

    send_registration_key(request, user, password, registration)

    return True

@to_response
def email_sent(request):
    return 'signup_email_sent.html'

@to_response
def complete_signup(request, key=None):
    from django.contrib.auth import login, authenticate

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'GET':
        if 'email' not in request.GET:
            raise Http404
        else:
            email = request.GET.get('email')
        if key:
            registration = get_object_or_404(
                Registration, key=key, user__email=email)
            if not registration.completed:
                registration.complete()
            else:
                if registration.user.password != '':
                    raise Http404
        else:
            input_form = InputKeyForm()
            if request.method == 'POST':
                post = request.POST.copy()
                input_form = InputKeyForm(post)
                if input_form.is_valid():
                    registration = get_object_or_404(
                        Registration, key=key, user__email=email)
                    if not registration.completed:
                        registration.complete()
                    else:
                        if registration.user.password != '':
                            raise Http404

    return HttpResponseRedirect(reverse('signup-success'))

# TODO:
# TODO: Cron que borre los registros mayores a 1 semana.

# FIXME:
# FIXME: ATENCIÓN: Ojo con la lógica de esta función, la estoy escribiendo sin
# FIXME: estar muy despierto, así que hay que chequear que realmente ande y no
# FIXME: tenga agujeros de seguridad. Especialmente con respecto al gonzo y la
# FIXME: posibilidad de setear passwords para otros usuarios.
"""
@to_response
def set_password(request, registration=None, key=None, email=None):
    if username != request.user.username:
        raise Http404
    if registration:
        passwd_form = SetPasswordForm(username=registration.user.username, key=registration.key)
    else:
        passwd_form = SetPasswordForm()
    if request.method == 'POST':
        post = request.POST.copy()
        user = get_object_or_404(User, username=post.get('username'))
        registration = get_object_or_404(
            Registration, user=user, key=post.get('key'))
        passwd_form = SetPasswordForm(post, key=key,
                                      username=registration.user.username)
        if passwd_form.is_valid():
            user.set_password(post.get('password'))
            user.save()
            return HttpResponseRedirect(reverse('signup-success'))
    return 'signup_passwd.html', {'registration': registration,
                                  'set_password_form': passwd_form}
"""

@to_response
def success(request):
    return 'signup_success.html'

def finish_registration(registration):
    registration.user.is_active = True
    registration.completed = True
    registration.user.save()
    registration.save()
    user.save()
    return True
