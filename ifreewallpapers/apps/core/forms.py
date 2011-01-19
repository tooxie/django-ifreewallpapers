# coding=UTF-8
from django.forms import Form, FileField, CharField, ChoiceField, EmailField, \
                         BooleanField, HiddenInput, Select, \
                         ValidationError, TextInput, FileInput
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from core.models import Resolution, Wallpaper

from md5 import md5

class UploadWallpaperForm(Form):
    image = FileField(widget=FileInput(attrs={'class': 'textbox'}))
    author = CharField(required=False, max_length=50, help_text=_(u"Optional"),
        widget=TextInput(attrs={'class': 'textbox'}))
    title = CharField(max_length=100,
        widget=TextInput(attrs={'class': 'textbox'}))
    tags = CharField(max_length=100,
        widget=TextInput(attrs={'class': 'textbox'}),
        help_text=_(u"A comma separated list of tags."))
    inappropriate = BooleanField(required=False)

    def clean_image(self):
        """
    Validates that the uploaded image doesn't exceeds the 10MB and it's in one
of the allowed formats:
    * PNG
    * GIF
    * JPG
        """
        image = self.cleaned_data['image']
        print image.content_type
        if image.size < settings.ALLOWED_IMAGE_SIZE:
            raise ValidationError(_(u"Image too big, \
                                     files over 10MB not allowed."))
        for allowed in settings.ALLOWED_CONTENT_TYPES:
            if image.content_type == allowed[0]:
                return image
        raise ValidationError(_(u"File type is not valid. \
                                 Allowed types are PNG, GIF and JPG."))

class DownloadWallpaperForm(Form):
    resolutions = CharField(label=_(u"Screen Size"),
        widget=Select(choices=(), attrs={'class': 'textbox'}))
    wallpaper = CharField(widget=HiddenInput)
    action = CharField(widget=HiddenInput, initial='download')
    gonzo = CharField(widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        if 'wallpaper' not in kwargs and len(args) == 0:
            raise ValidationError(_(u"Lack of wallpaper to get resolutions \
                                      for."))
        else:
            try:
                self.wallpaper = kwargs['wallpaper']
                del(kwargs['wallpaper'])
            except:
                self.wallpaper = Wallpaper.objects.get(
                    slug=args[0]['wallpaper'])

            self.width, self.height = self.wallpaper.get_size().split('x')
            initial = {'wallpaper': self._wallpaper(),
                       'gonzo': self._gonzo()}
            kwargs['initial'] = initial
        super(DownloadWallpaperForm, self).__init__(*args, **kwargs)
        self.fields['resolutions'].widget.choices = self._resolution_choices()

    def _wallpaper(self):
        return self.wallpaper.slug

    def _gonzo(self):
        return md5('%(id)i-%(slug)s-%(salt)s' % \
                  {'id': self.wallpaper.id,
                   'slug': self.wallpaper.slug,
                   'action': 'download',
                   'salt': settings.SECRET_KEY}).hexdigest()

    def _resolution_choices(self):
        resolutions = self.wallpaper.get_display_resolutions()
        """
        queryset = Resolution.objects.filter(
            type__ne='ns').filter(
                width__lte=self.width, height__lte=self.height).order_by(
                    '-downloads', 'type', '-width', '-height')
        """
        previous = ''
        choices, group = [], []
        # Si resolutions es un Queryset, entonces tengo que usar count(), pero
        # si es List, uso len().
        how_many = resolutions.count() # len(resolutions)
        choices.append(('', _(u'--- Choose Yours ---')))

        for index, resolution in enumerate(resolutions):
            if previous == '':
                previous = resolution.get_type_display()

            if previous != resolution.get_type_display():
                choices.append((previous, group))
                group = []

            group.append((str(resolution), resolution))

            if index + 1 == how_many:
                choices.append((resolution.get_type_display(), group))

            previous = resolution.get_type_display()
        return choices

    def clean_resolutions(self):
        selected = self.cleaned_data['resolutions']
        for resolution in self.wallpaper.get_display_resolutions():
            if str(resolution) == selected:
                return selected
        raise ValidationError(_(u"Your choice is not valid, please select one \
                                 from the list."))

    def clean_gonzo(self):
        gonzo = self.cleaned_data['gonzo']
        if gonzo != self._gonzo():
            raise ValidationError(_(u"Please verify the data."))
        return gonzo

class SendWallpaperForm(Form):
    friends_name = CharField(label=_(u"Friend's name"),
        widget=TextInput(attrs={'class': 'textbox'}))
    friends_email = EmailField(label=_(u"Friend's e-mail"),
        widget=TextInput(attrs={'class': 'textbox'}))
    your_name = CharField(label=_(u"Your name"), required=False,
        widget=TextInput(attrs={'class': 'textbox'}))
    your_email = EmailField(label=_(u"Your e-mail"), required=False,
        widget=TextInput(attrs={'class': 'textbox'}))
    about = CharField(widget=HiddenInput)
    action = CharField(widget=HiddenInput, initial='tellafriend')
    gonzo = CharField(widget=HiddenInput)

    def clean_your_name(self):
        data = self.cleaned_data
        if hasattr(self, 'user'):
            if not self.user.first_name or not self.user.last_name:
                if not data.get('your_name'):
                    raise ValidationError(_(u"This field is required"))
        return data.get('your_name')

    def clean_your_email(self):
        data = self.cleaned_data
        if hasattr(self, 'user'):
            if not self.user.email:
                if not data.get('your_email'):
                    raise ValidationError(_(u"This field is required"))
        return data.get('your_email')

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs['user']
            del(kwargs['user'])
        if 'wallpaper' in kwargs:
            self.wallpaper = kwargs['wallpaper']
            del(kwargs['wallpaper'])

        super(SendWallpaperForm, self).__init__(*args, **kwargs)

        try:
            if self.user.is_authenticated():
                if self.user.email:
                    del(self.fields['your_email'])
                if self.user.first_name and self.user.last_name:
                    del(self.fields['your_name'])
            self.fields['about'].initial = self.wallpaper.slug
            self.fields['gonzo'].initial = self._gonzo()
        except Exception, e:
            print e

    def _gonzo(self):
        return md5('%(id)i-%(slug)s-%(salt)s' % \
                  {'id': self.wallpaper.id,
                   'slug': self.wallpaper.slug,
                   'salt': settings.SECRET_KEY}).hexdigest()

    def clean_gonzo(self):
        gonzo = self.cleaned_data['gonzo']
        if gonzo != self._gonzo():
            raise ValidationError(_(u"Please verify the data."))
        return gonzo

class AdoptWallpaperForm(Form):
    author = CharField(required=False, max_length=50, help_text=_(u"Optional"),
        widget=TextInput(attrs={'class': 'textbox'}))
    title = CharField(max_length=100,
        widget=TextInput(attrs={'class': 'textbox'}))
    tags = CharField(max_length=100,
        help_text=_(u"A comma separated list of tags."),
        widget=TextInput(attrs={'class': 'textbox'}))
    inappropriate = BooleanField(required=False)
    gonzo = CharField(widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        if 'wallpaper' in kwargs:
            self.wallpaper = kwargs['wallpaper']
            del(kwargs['wallpaper'])

        super(AdoptWallpaperForm, self).__init__(*args, **kwargs)

        if self.wallpaper:
            self.fields['author'].initial = self.wallpaper.author
            self.fields['title'].initial = self.wallpaper.title
            self.fields['tags'].initial = ''
            for tag in self.wallpaper.tags:
                self.fields['tags'].initial += str(tag)
            self.fields['inappropriate'].initial = self.wallpaper.inappropriate
            self.fields['gonzo'].initial = self._gonzo()

    def _gonzo(self):
        return md5('%(id)i-%(slug)s-%(salt)s' % \
                  {'id': self.wallpaper.id,
                   'slug': self.wallpaper.slug,
                   'salt': settings.SECRET_KEY}).hexdigest()

    def clean_gonzo(self):
        gonzo = self.cleaned_data['gonzo']
        if gonzo != self._gonzo():
            raise ValidationError(_(u"Please verify the data."))
        return gonzo

class EmailMeWhenSavedWallpaperForm(Form):
    email = EmailField(widget=TextInput(attrs={'class': 'textbox'}))
    about = CharField(widget=HiddenInput)
    action = CharField(widget=HiddenInput, initial='letmeknow')
    gonzo = CharField(widget=HiddenInput)

    # FIXME:
    # FIXME: DRY violation alert!
    # FIXME: Estoy repitiendo el hack de pasar usuario y/o wallpaper al form
    # FIXME: demasiadas veces. Como puedo abstraer esto?
    def __init__(self, *args, **kwargs):
        # Si no hay post...
        if 'user' in kwargs:
            self.user = kwargs['user']
            del(kwargs['user'])
        if 'wallpaper' in kwargs:
            self.wallpaper = kwargs['wallpaper']
            del(kwargs['wallpaper'])

        super(EmailMeWhenSavedWallpaperForm, self).__init__(*args, **kwargs)

        try:
            if self.user.is_authenticated() and self.user.email:
                # self.fields['email'].widget = HiddenInput()
                self.fields['email'].initial = self.user.email
        except Exception, e:
            print e
        try:
            self.fields['about'].initial = self.wallpaper.slug
            self.fields['gonzo'].initial = self._gonzo()
        except Exception, e:
            print e

    # FIXME:
    # FIXME: DRY violation alert!
    # FIXME: Debería crear un FormWithGonzo?
    def _gonzo(self):
        return md5('%(id)i-%(slug)s-%(salt)s' % \
                  {'id': self.wallpaper.id,
                   'slug': self.wallpaper.slug,
                   'salt': settings.SECRET_KEY}).hexdigest()

    def clean_gonzo(self):
        gonzo = self.cleaned_data['gonzo']
        if gonzo != self._gonzo():
            raise ValidationError(_(u"Please verify the data."))
        return gonzo

class ManageWallpaperForm(Form):
    tags = CharField(_(u'Tags'), required=False,
        widget=TextInput(attrs={'class': 'textbox'}))
    author = CharField(_(u'Author'), required=False,
        widget=TextInput(attrs={'class': 'textbox'}))
    inappropriate = BooleanField(required=False, label=_(u'Inappropriate'),
        help_text=_(u"Check this if the image contains nudity or violence."))
    """
    draft = BooleanField(
        help_text=_(u"Check this if the wallpaper is not complete of if you \
                      don't want to publish it yet."))
    """
    wallpaper = CharField(widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        if 'wallpaper' in kwargs:
            try:
                self.wallpaper = Wallpaper.objects.get(
                    slug=kwargs.get('wallpaper', None))
            except Exception, e:
                print e
            if self.wallpaper:
                tags = ''
                for tag in self.wallpaper.tags:
                    tags += tag.name + ', '
                tags = tags[:-2]
                initial = {'wallpaper': self.wallpaper.slug,
                           'tags': tags,
                           'author': self.wallpaper.author,
                           'inappropriate': self.wallpaper.inappropriate,
                           'gonzo': self._gonzo()}
                kwargs['initial'] = initial
                del(kwargs['wallpaper'])
        super(ManageWallpaperForm, self).__init__(*args, **kwargs)

    def _gonzo(self):
        return md5('%(id)i-%(slug)s-%(salt)s' % \
                  {'id': self.wallpaper.id,
                   'slug': self.wallpaper.slug,
                   'salt': settings.SECRET_KEY}).hexdigest()

    def clean_gonzo(self):
        gonzo = self.cleaned_data['gonzo']
        if gonzo != self._gonzo():
            raise ValidationError(_(u"Please verify the data."))
        return gonzo
