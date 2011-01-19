# coding=UTF-8
from profile import settings as _settings
from profile.avatars import handle_avatar
from profile.forms import SignupForm, UploadAvatarForm, RetrieveImageForm, \
                          ChooseWallpaperForm, PasswordResetForm, LoginForm, \
                          DummyAvatarForm, PasswordChangeForm, EmailChangeForm
from profile.models import Avatar, Profile

from utils import next
from utils.contenttype import get_ext
from utils.decorators import render_response
from utils.exceptions import NotImplementedError

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _ # FIXME: Intentar sacar de acá

import os # FIXME: Intentar sacar de acá

to_response = render_response('profile/')

@login_required
@to_response
def overview(request):
    try:
        profile = request.user.get_profile()
    except:
        profile = Profile()
        profile.user = request.user
        profile.save()
    return 'overview.html', {'profile': profile,
                             'groups': profile.get_groups()}

@to_response
def public(request, username):
    return 'public.html', {'profile': request.user.get_profile()}

@login_required
@to_response
def avatar(request):
    upload = UploadAvatarForm()
    retrieve = RetrieveImageForm()
    choose = ChooseWallpaperForm()
    is_valid, rerrors = False, []
    if request.method == 'POST':
        post = request.POST.copy()
        profile = request.user.get_profile()
        if post.get('action') == 'upload':
            upload = UploadAvatarForm(post, request.FILES)
            if upload.is_valid():
                ufile, uerrors = handle_upload(request.FILES['file'])
                avatar = handle_avatar(ufile, profile)
                set_avatar(avatar.id, request.user.get_profile())
                return HttpResponseRedirect(reverse('account-index'))
        elif post.get('action') == 'url':
            retrieve = RetrieveImageForm(post)
            if retrieve.is_valid():
                rfile, rerrors = retrieve_url(post.get('url'))
                if not rerrors:
                    avatar = handle_avatar(rfile, profile)
                    set_avatar(avatar, request.user.get_profile())
                    return HttpResponseRedirect(reverse('account-index'))
        elif post.get('action') == 'wallpaper':
            choose = ChooseWallpaperForm(post)
            return pick_wallpaper(post.get('token'))
        elif post.get('action') == 'previous':
            if post.get('avatar') != None:
                set_avatar(post.get('avatar'), request.user.get_profile())
                return HttpResponseRedirect(reverse('account-index'))
    return 'avatar.html', {'upload_form': upload, 'retrieve_form': retrieve,
                           'choose_form': choose, 'retrieve_errors': rerrors}

def handle_upload(uploaded_file):
    errors = []
    ext = '.%s' % get_ext(uploaded_file.content_type)
    tmp = open(os.path.join(_settings.AVATARS_DIR, 'tmp',
                            get_random_filename(suffix=ext)), 'w+b')
    try:
        tmp.write(uploaded_file.read(_settings.MAX_AVATAR_SIZE + 100))
        if len(open(tmp.name, 'r').read()) > _settings.MAX_AVATAR_SIZE:
            errors.append(_(u'File size too big.')) # FIXME: Intentar sacar de acá
            os.remove(tmp.name)
    except Exception, e:
        errors.append(_(u'Unknown error occurred.')) # FIXME: Intentar sacar de acá
    tmp.close()
    return (open(tmp.name, 'r'), errors)

def retrieve_url(url):
    import urllib2

    errors = []
    ext = '.%s' % get_ext(url, True)
    tmp = open(os.path.join(_settings.AVATARS_DIR, 'tmp',
                            get_random_filename(suffix=ext)), 'w+b')
    try:
        headers = {'User-Agent': settings.VALIDATOR_USER_AGENT}
        request = urllib2.Request(url, headers=headers)
        # for h in urllib2.urlopen(request).info().headers: print h.strip()
        tmp.write(urllib2.urlopen(request).read(
            _settings.MAX_AVATAR_SIZE + 100))
        if len(open(tmp.name, 'r').read()) > _settings.MAX_AVATAR_SIZE:
            # FIXME:
            # FIXME: Habrá manera de sacar esta traducción de acá?
            errors.append(_(u'File size too big.')) # FIXME: Intentar sacar de acá
            os.remove(tmp.name)
    except Exception, e:
        print e
        errors.append(_(u'Unknown error occurred.')) # FIXME: Intentar sacar de acá
    tmp.close()
    return (open(tmp.name, 'r'), errors)

def get_random_filename(suffix=''):
    from tempfile import NamedTemporaryFile

    tmpf = NamedTemporaryFile(suffix=suffix)
    tmpf.close()
    return tmpf.name[tmpf.name.rfind('/') + 1:][3:]

def set_avatar(avatar, profile):
    if isinstance(avatar, Avatar):
        profile.avatar = avatar
    else:
        if avatar == '0':
            profile.avatar = None
        else:
            try:
                avatar = Avatar.objects.get(id=avatar)
            except Exception, e:
                print e
                return False
            profile.avatar = avatar
    profile.save()
    return True

@login_required
@to_response
def make_avatar(request, *args, **kwargs):
    model = kwargs.get('model')
    match = kwargs.get('match')
    file = kwargs.get('file')
    keyword = kwargs.get('keyword')
    qargs = {match: keyword}
    instance = model.objects.get(**qargs)
    file_path = instance.__getattribute__(file)
    if not file_path.startswith(settings.MEDIA_ROOT):
        file_path = settings.MEDIA_ROOT + file_path
    avatar = handle_avatar(open(file_path, 'r+b'),
                           request.user.get_profile(), remove_original=False)
    set_avatar(avatar.id, request.user.get_profile())
    return HttpResponseRedirect(next(request))

# DEPRECATED: Not in use.
@login_required
@to_response
def manage_avatars(request):
    pass

@login_required
def delete_avatar(request):
    request.user.get_profile().avatar.delete()
    return HttpResponseRedirect(reverse('account-index'))

@login_required
@to_response
def change_email(request):
    change = EmailChangeForm()
    if request.method == 'POST':
        post = request.POST.copy()
        change = EmailChangeForm(post)
        if change.is_valid():
            pass
    return 'email.html', {'change_form': change}

@login_required
@to_response
def change_password(request):
    change = PasswordChangeForm(user=request.user)
    if request.method == 'POST':
        post = request.POST.copy()
        user = request.user
        if user.username == post.get('username'):
            change = PasswordChangeForm(post, user=user)
            if change.is_valid():
                user.set_password(post.get('new_password'))
                return HttpResponseRedirect(reverse('account-index'))
        else:
            return logout(request)
    return 'password_change.html', {'change_form': change}

@to_response
def lost_password(request):
    from profile.profileutils import keygen

    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    forgot = PasswordResetForm()
    if request.method == 'POST':
        post = request.POST.copy()
        forgot = PasswordResetForm(post)
        if forgot.is_valid():
            email = post.get('email')
            user = User.objects.get(email=email, username=email)
            passwd = keygen(user)[:8]
            user.set_password(passwd)
            user.save()
            send_password(user, passwd)
            return 'email_sent.html'
    return 'lost_password.html', {'remind_form': forgot}

# FIXME:
# FIXME: ¿No debería ir esto en el módulo signup?
def send_password(user, passwd):
    from sendmail import send_mail

    from django.template import loader, Context

    recipient = '<%(name)s> %(email)s' % {'name': user.get_full_name(),
                                          'email': user.email}
    recipient = user.email
    sender = '<%(name)s> %(email)s' % {'name': settings.DEFAULT_FROM_NAME,
                                       'email': settings.DEFAULT_FROM_EMAIL}
    sender = settings.DEFAULT_FROM_EMAIL
    subject = _(u'Password recovery')
    message = loader.get_template(
        'profile/' + settings.EMAIL_RECOVER_PASSWORD).render(
            Context(
                {'passwd': passwd}))
    send_mail(recipient_list=[recipient], from_email=sender,
              subject=subject, message=message)

@login_required
@to_response
def location(request):
    raise NotImplementedError('profile.views.accountviews.location')
    return 'location.html', {'profile': request.user.get_profile()}

@to_response
def login(request):
    from django.contrib.auth import authenticate, login

    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    error = ''
    if request.method == 'POST':
        post = request.POST.copy()
        user = authenticate(username=post.get('username'),
                            password=post.get('password'))
        if user:
            if user.is_active:
                login(request, user)
            else:
                return HttpResponseRedirect(
                    reverse('account-disabled',
                            kwargs={'username': post.get('username')}))
            return HttpResponseRedirect(next(request))
        else:
            error = 'Contraseña incorrecta.'

    login = LoginForm()
    return 'login.html', {'login_form': login, 'next': next(request),
        'error': error}

@to_response
def disabled(request, username):
    user = User.objects.get(username=username)
    if not user.is_active:
        return 'disabled.html', {'username': username}
    raise Http404

@to_response
def logout(request):
    from django.contrib.auth import logout

    logout(request)
    return HttpResponseRedirect(next(request))

@login_required
@to_response
def change_personal(request):
    from profile.models import Field, FieldData, FieldChoice, TextData, CharData

    from django.contrib.contenttypes.models import ContentType

    if request.method == 'POST':
        post = request.POST.copy()
        profile = request.user.get_profile()
        modified_multiple_fields = [] # Lista de los checkboxes seleccionados.
        # Permite luego eliminar los que hayan sido des-chequeados.
        """Por cada campo tomo su id, si es múltiple obtengo sus choices,
    sino instancio su contenido. Si es Single Choice elimino los rastros de la
    opción antes elegida. Por último instancio el dato y elimino los campos que
    hayan sido dejado vacíos."""
        for profile_field in post:
            choice_id = None
            try:
                field_id = int(profile_field)
            except:
                field_id, choice_id = profile_field.split('-')
            try:
                field = Field.objects.get(id=field_id)
            except:
                raise Http404
            if field.is_multiple():
                if not choice_id:
                    choice_id = post.get(profile_field)
                field_content = FieldChoice.objects.get(id=choice_id)
                modified_multiple_fields.append(field_content.id)
            else:
                if field.is_long_text():
                    field_content, created = TextData.objects.get_or_create(
                        content=post.get(profile_field))
                else:
                    field_content, created = CharData.objects.get_or_create(
                        content=post.get(profile_field))
            ctype = ContentType.objects.get_for_model(field_content)
            field_content.save()
            # FIXME:
            # FIXME: Como mierda hago para saber si el field es público o no?
            public = True
            if field.is_single_choice():
                for chosen in FieldData.objects.filter(owner=profile,
                    content_type=ctype, field__id=field.id, field__type='SC'):
                    chosen.delete()
            # FIXME:
            # FIXME: Qué va a pasar cuando la base tenga la restricción de los
            # FIXME: campos que son únicos y esto intente crear un objeto con
            # FIXME: los mismos datos que otro? Testear.
            data, created = FieldData.objects.get_or_create(
                content_type=ctype, object_id=field_content.id, owner=profile,
                defaults={'field': field, 'public': public})
            if post.get(profile_field, '') == '':
                data.delete()
            field = Field.objects.get(id=field_id)
        # Elimino los campos que el usuario deseleccionó.
        ctype = ContentType.objects.get_for_model(FieldChoice)
        for field in FieldData.objects.filter(content_type=ctype,
                                              owner=profile, field__type='MC'):
            if field.data.id not in modified_multiple_fields:
                field.delete()
        return HttpResponseRedirect(reverse('account-change_personal'))
    return 'change_personal.html'

