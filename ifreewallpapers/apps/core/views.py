# coding=UTF-8
from core.rates import get_rate, do_rate # FIXME
from core.forms import (AdoptWallpaperForm, DownloadWallpaperForm,
    EmailMeWhenSavedWallpaperForm, ManageWallpaperForm SendWallpaperForm,
    UploadWallpaperForm,)
from core.models import Wallpaper, Waiting
# from utils.exceptions import NotImplementedError
# FIXME:
from favs.utils import is_this_fav
# FIXME: Refactoring de favoritos. Reubicar la función is_this_fav.
from utils.decorators import render_response
to_response = render_response('core/')

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.conf import settings
from django.template.defaultfilters import slugify

from datetime import datetime
from os import path

@login_required
@to_response
def upload(request):
    """
    Vista que despliega y valida el formulario para subir wallpapers.
    """
    upload_form = UploadWallpaperForm()
    if request.method == "POST":
        post = request.POST.copy()
        upload_form = UploadWallpaperForm(post, request.FILES)
        if upload_form.is_valid():
            if handle_upload(request):
                return HttpResponseRedirect(reverse('upload_successful'))
    return 'upload.html', {'form': upload_form}

def handle_upload(request):
    """
    Función que se encarga de manipular el wallpaper una vez en el servidor.
    """
    post = request.POST.copy()
    try:
        wallpaper = Wallpaper()
        wallpaper.author = post.get('author')
        wallpaper.title = post.get('title')
        wallpaper.uploader = request.user
        wallpaper.save()
        wallpaper.tags = post.get('tags')
    except Exception, e:
        print e
        return None
    try:
        file = request.FILES['image']
        filename = path.join(
            settings.UPLOAD_DIR, request.user.get_profile().slug,
            '%s.%s' % (wallpaper.slug, get_extension(file.content_type)))
        destination = open(filename, 'w')
        if file.multiple_chunks():
            for chunk in file.chunks():
                destination.write(chunk)
        else:
            destination.write(file.read())
    except Exception, e:
        print e
        return None
    wallpaper.file = filename
    wallpaper.save()
    return True

def get_extension(content_type):
    for allowed in settings.ALLOWED_CONTENT_TYPES:
        if content_type == allowed[0]:
            return allowed[1]
    return None

@login_required
@to_response
def upload_successful(request):
    """
    Vista que muestra un mensaje de éxito en caso de que el wallpaper se suba
correctamente, confirmando los datos que el usuario ingresó.
    """
    wallpaper = request.user.wallpaper_set.order_by('-date')[:1].get()
    if ((datetime.now() - wallpaper.date).seconds / 60) > 1:
        raise Http404
    return 'upload_successful.html', {'file': wallpaper.file,
                                      'author': wallpaper.author,
                                      'title': wallpaper.title,
                                      'slug': wallpaper.slug}

@to_response
def wallpaper(request, slug=None):
    # letmeknow
    when_saved, send_wallpaper = None, None
    post = {}
    if request.method == "POST":
        post = request.POST.copy()
    # FIXME:
    # FIXME: Se llama esta misma función tanto cuando se ve un wallpaper como
    # FIXME: cuando se va a descargarlo. Esto no debería ser así porque está
    # FIXME: creando mucha incoherencia y contorciones de código.
    if slug:
        wallpaper = get_object_or_404(Wallpaper, slug=slug)
    else:
        # Cuando quiero descargarlo debe haber sido perdonado previamente.
        wallpaper = get_object_or_404(Wallpaper, slug=post.get('wallpaper', None),
                                      forgiven=True)
    # Valido acciones extras que pueda querer el usuario.
    if 'action' in post:
        if post.get('action') == 'tellafriend':
            send_wallpaper = SendWallpaperForm(post, wallpaper=wallpaper)
            if send_wallpaper.is_valid():
                return tell_a_friend(request, wallpaper)
        elif post.get('action') == 'letmeknow':
            when_saved = EmailMeWhenSavedWallpaperForm(post,
                                                       wallpaper=wallpaper)
            if when_saved.is_valid():
                return let_me_know(request, wallpaper)
    # Si el wallpaper está perdonado es muy probable que esté buscando
    # descargarlo.
    if wallpaper.forgiven and request.method == "POST" and \
            post.get('action') == 'download':
        form = DownloadWallpaperForm(post)
        if form.is_valid():
            # Hack alert!
            width, height = post['resolutions'].split('x')
            resolution = wallpaper.resolution.__class__.objects.get(
                width=width, height=height)
            resolution.downloads += 1
            resolution.save()
            return get_response_and_file(wallpaper, str(resolution))
    else:
        form = DownloadWallpaperForm(wallpaper=wallpaper)
        if not wallpaper.uploader == request.user:
            wallpaper.viewed += 1
            wallpaper.save()
    # canadopt?
    # FIXME:
    # FIXME: can_adopt va en el profile.
    can_adopt = True
    if request.user.is_authenticated():
        last_adoption = Wallpaper.objects.filter(
            uploader=request.user.id).exclude(
                adopted=None).order_by(
                    '-adopted')[:1]
        if last_adoption:
            if (datetime.now() - last_adoption[0].adopted).days < 1:
                can_adopt = False
    # tellafriend
    if not send_wallpaper:
        send_wallpaper = SendWallpaperForm(user=request.user,
                                           wallpaper=wallpaper)
    # letmeknow
    if Waiting.objects.filter(wallpaper=wallpaper, user=request.user.id,
                              sent=False).count() == 0:
            when_saved = EmailMeWhenSavedWallpaperForm(user=request.user,
                                                       wallpaper=wallpaper)
    # rating
    # FIXME:
    # FIXME: Debería esto ir en el usuario?
    rates, my_rating = get_rate(wallpaper, request.user)
    # FIXME:
    # FIXME: Sacar esto de aca.
    # FIXME: Este código es para saber si el usuario ya votó este wallpaper.
    # FIXME: El problema es que corresponde a userprofile, pero todavía no lo
    # FIXME: puedo modificar.
    from limbo.models import Decision
    # FIXME:
    # FIXME: Debería mostrarle al usuario lo que eligió, no simplemente
    # FIXME: informarle que votó además de permitirle cambiar el voto.
    i_voted = Decision.objects.filter(
        judge=request.user.id, wallpaper=wallpaper).count()
    return 'wallpaper.html', \
          {'wallpaper': wallpaper, 'resolutions_form': form,
           'was_voted_on': i_voted, 'uploaded_by': _by(wallpaper),
           'random_slug': wallpaper.random_slug(
                forgiven=wallpaper.forgiven, user=request.user,
                exclude=wallpaper.slug),
           'let_me_know': when_saved, 'send_form': send_wallpaper,
           'see_also': get_related(request, wallpaper), 'can_adopt': can_adopt,
           'possible_rates': rates, 'i_rated': my_rating,
           'is_fav': is_this_fav(wallpaper, request.user, bool=True)}

# FIXME:
# FIXME: Sacar el html del uploaded by de la vista.
def _by(wallpaper):
    if not wallpaper.uploader:
        return False
    return '<a href="%(link)s">%(username)s</a>' % \
        {'link': reverse('profile',
            kwargs={'slug': wallpaper.uploader.get_profile().slug}),
         'username': wallpaper.uploader.get_full_name()}

@to_response
def manage_wallpaper(request, slug):
    wallpaper = get_object_or_404(Wallpaper, slug=slug)
    form = ManageWallpaperForm(wallpaper=slug)
    if request.method == "POST":
        post = request.POST.copy()
        form = ManageWallpaperForm(post)
        if form.is_valid():
            if 'inappropriate' in post:
                wallpaper.inappropriate = True
            else:
                wallpaper.inappropriate = False
            wallpaper.author = post.get('author')
            wallpaper.save()
            wallpaper.tags = post.get('tags')
            return HttpResponseRedirect(reverse('account-index'))
    return 'manage.html', {'wallpaper': wallpaper, 'manage': form}

# TODO:
# TODO: Implementar función que permite orfanar un wallpaper.
@login_required
@to_response
def orphan(request):
    if request.method == 'POST':
        post = request.POST.copy()
        wallpaper = get_object_or_404(Wallpaper, slug=post.get('wallpaper'),
                                      uploader=request.user)
        if 'confirm' in post:
            # FIXME:
            # FIXME: ~INCOMPLETE
            wallpaper.uploader = None
            wallpaper.save()
    else:
        raise Http404
    return 'orphan.html', {'wallpaper': wallpaper}

def get_related(request, wallpaper):
    count = wallpaper.comments_count
    if not count:
        how_many = 4
    else:
        # Aumentar una línea (2 wallpapers) cada 3 comentarios.
        how_many = (wallpaper.comments_count / 3 + 1) * 2 + 4
    if request.user.is_authenticated():
        user = request.user
    else:
        user = None
    see_also = Wallpaper.objects.filter(
        forgiven=wallpaper.forgiven).exclude(
            id=wallpaper.id).order_by('?')[:how_many]
    return see_also

def get_response_and_file(wallpaper, resolution):
    from django.http import HttpResponse
    from mimetypes import guess_type

    file = open(wallpaper.get_for_resolution(resolution), 'r')
    wallpaper.downloads += 1
    wallpaper.save()
    filename = file.name[file.name.rfind('/')+1:]
    response = HttpResponse(file.read(), mimetype=guess_type(file.name)[0])
    response['Content-Disposition'] = 'attachment; filename=' + \
        filename[:filename.rfind('.')] + '-' + str(resolution) + \
            filename[filename.rfind('.'):]
    return response

def tell_a_friend(request, wallpaper):
    import email

    if request.method == "POST":
        post = request.POST
        user = request.user
        sender, recipient = '', ''
        from_name = post.get('your_name')
        from_email = post.get('your_email')
        to_name = post.get('friends_name')
        if user.is_authenticated():
            if user.first_name or user.last_name:
                from_name = '%(first_name)s %(last_name)s' % \
                    {'first_name': request.user.first_name,
                     'last_name': request.user.last_name}
            if user.email:
                from_email = user.email
        if email.tell_a_friend(about=wallpaper,
            recipient=(to_name, post.get('friends_email')),
                sender=(from_name, from_email)):
            if wallpaper.forgiven:
                home = reverse('home')
            else:
                home = reverse('limbo')
            return 'email_sent.html', {'next': post.get('next', '/'),
                'slug': wallpaper.slug, 'name': to_name, 'home': home}
    raise Http404

@login_required
@to_response
def adopt(request, slug):
    if not request.method == "POST" or not request.user.is_authenticated():
        raise Http404
    wallpaper = get_object_or_404(Wallpaper, slug=slug, adopted=None)
    post = request.POST
    adopt_form = AdoptWallpaperForm(wallpaper=wallpaper)
    if 'confirm' in post:
        adopt_form = AdoptWallpaperForm(post, wallpaper=wallpaper)
        if adopt_form.is_valid():
            if 'inappropriate' in post:
                is_inappropriate = True
            else:
                is_inappropriate = False
            if wallpaper.adopt(request.user, inappropriate=is_inappropriate,
                               title=post['title'], tags=post['tags']):
                # Felicitaciones! Es un wallpaper! =)
                return HttpResponseRedirect(
                    reverse('view_wallpaper', kwargs={'slug': wallpaper.slug}))
    context = {'wallpaper': wallpaper, 'adopt_form': adopt_form}
    return 'adopt.html', context

# TODO:
# TODO: Implementar el aviso de salvación a todos los usuarios que lo pidieron.
# TODO:
# TODO: Implementar algoritmo que decide cuando un wallpaper es salvado.
def let_me_know(request, wallpaper):
    if request.user.is_authenticated():
        user = request.user
    else:
        user = None
    # FIXME:
    # FIXME: Esta variable no la uso para nada.
    in_queue, created = Waiting.objects.get_or_create(
        wallpaper=wallpaper, email=request.POST['email'], sent=False,
        defaults={'user': user})
    return HttpResponseRedirect(
        reverse('view_wallpaper', kwargs={'slug': wallpaper.slug}))

@login_required
@to_response
def rate(request, rate, slug):
    return do_rate(request.user, rate, slug)

# FIXME:
# FIXME: Hardcoding alert!
@login_required
def toggle_fav(request, slug):
    from favs.models import Favourite

    wallpaper = get_object_or_404(Wallpaper, slug=slug, forgiven=True)
    fav = is_this_fav(wallpaper, request.user)
    fav.toggle()
    return HttpResponseRedirect(
        reverse('view_wallpaper', kwargs={'slug': slug}))
