# coding=UTF-8
from utils import do_gonzo

from django.forms import Form, ImageField, URLField, CharField, EmailField, \
                         ValidationError, PasswordInput, TextInput, \
                         HiddenInput
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User


class SignupForm(Form):
    """
    username = CharField(max_length=255, min_length=3, label=_(u'Username'),
        widget=TextInput(attrs={'class': 'textbox'}))
    """
    first_name = CharField(label=_(u'First Name'), max_length=50,
        widget=TextInput(attrs={'class': 'textbox'}))
    last_name = CharField(label=_(u'Last Name'), max_length=50,
        widget=TextInput(attrs={'class': 'textbox'}))
    email = EmailField(label=_('e-Mail'), widget=TextInput(
        attrs={'class': 'textbox'}))
    """
    password1 = CharField(min_length=6, label=_('Password'),
        widget=PasswordInput(render_value=False, attrs={'class': 'textbox'}))
    password2 = CharField(min_length=6, label=_('Password (again)'),
        widget=PasswordInput(render_value=False, attrs={'class': 'textbox'}))
    """

    """
    def clean_username(self):
        \"""
        Verify that the username isn't already registered
        \"""
        username = self.cleaned_data.get("username")
        if not set(username).issubset(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"):
            raise ValidationError(_("That username has invalid characters. The\
                                     valid values are letters, numbers and\
                                     underscore."))

        if User.objects.filter(username__iexact=username).count() == 0:
            return username
        else:
            raise ValidationError(_("The username is already registered."))
    """

    """
    def clean(self):
        \"""
        Verify that the 2 passwords fields are equal
        \"""
        data = self.cleaned_data
        if data.get("password1") == data.get("password2"):
            return self.cleaned_data
        else:
            raise ValidationError(_("The passwords inserted are different."))
    """

    def clean_email(self):
        """
        Verify that the email exists
        """
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).count():
            raise ValidationError(_("That e-mail has been already used."))
        return email


# DEPRECATED: No usar, será eliminado.
class InputKeyForm(Form):
    email = EmailField(_(u'e-Mail'))
    key = CharField(label=_(u'Key'), max_length=32)

    def clean(self):
        from profile.models import Registration

        email = self.cleaned_data.get('email')
        key = self.cleaned_data.get('key')
        if len(key) != 32:
            raise forms.ValidationError(_(u'Invalid key.'))
        try:
            registration = Registration.objects.get(
                key=key, completed=False, user__email=email)
        except Registration.DoesNotExist:
            raise forms.ValidationError(_(u'Invalid key.'))
        return key


# DEPRECATED: No usar, será eliminado.
class SetPasswordForm(Form):
    password = CharField(label=_(u'Password'), max_length=50,
        widget=PasswordInput)
    password_again = CharField(label=_(u'Type it again'), max_length=50,
        widget=PasswordInput)
    username = CharField(widget=HiddenInput())
    key = CharField(max_length=32, widget=HiddenInput())
    gonzo = CharField(widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        self.initial = {}
        if 'username' in kwargs:
            self.initial['username'] = kwargs.get('username')
            del kwargs['username']
        if 'key' in kwargs:
            self.initial['key'] = kwargs.get('key')
            del kwargs['key']
        self.initial['gonzo'] = do_gonzo(self.initial.get('username', ''),
                                         self.initial.get('key', ''))
        kwargs['initial'] = self.initial
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        passwd = self.cleaned_data.get('password')
        passwd_ = self.cleaned_data.get('password_again')
        gonzo = self.cleaned_data.get('gonzo')

        if passwd == passwd_:
            if len(passwd) < 6:
                raise ValidationError(_(u"Chosen password is too short. It \
                    must be at least 6 characters long."))
            chars = []
            for char in passwd:
                if char not in chars:
                    chars.append(char)
            if len(chars) < 3:
                raise ValidationError(_(u"The password muust contain at least \
                    3 different characters."))
        # FIXME:
        # FIXME: Testear: No está llegando la key. Supongo que no llegó la
        # FIXME: primera vez y entonces las veces consecutivas no tuvieron
        # FIXME: acceso para chequearlo. Hacer todo el proceso de nuevo,
        # FIXME: debería andar. Sino arreglar, la concha de la lora.
        if gonzo != do_gonzo(self.initial.get('username', ''),
                                              self.initial.get('key', '')):
            raise ValidationError(_(u"Unknown error occurred."))


class LoginForm(Form):
    username = CharField(label=_(u'e-Mail address'),
        widget=TextInput(attrs={'class': 'textbox'}))
    password = CharField(label=_(u'Password'),
        widget=PasswordInput(attrs={'class': 'textbox'}))

    """
    def clean(self):
        from django.contrib.auth import authenticate, login

        data = self.cleaned_data
        user = authenticate(username=data.get('username'), password)
    """


class PasswordResetForm(Form):
    email = EmailField(widget=TextInput(attrs={'class': 'textbox'}))

    def clean_email(self):
        """
        Verify that the email or the user exists
        """
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(username=email, email=email)
        except Exception, e:
            print e
            raise ValidationError(_(u"There's no user with that e-mail"))

        return email


class PasswordChangeForm(Form):
    old_password = CharField(label=_(u'Old Password'),
        widget=PasswordInput(attrs={'class': 'textbox'}))
    new_password = CharField(label=_(u'New Password'),
        widget=PasswordInput(attrs={'class': 'textbox'}))
    new_password_again = CharField(label=_(u'New Password Again'),
        widget=PasswordInput(attrs={'class': 'textbox'}))
    username = CharField(widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            initial = {'username': kwargs.get('user').username}
            kwargs['initial'] = initial
            del kwargs['user']
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Verify that the 2 passwords fields match
        """
        from django.contrib.auth import authenticate

        data = self.cleaned_data
        if data.get("new_password") != data.get("new_password_again"):
            raise ValidationError(_(u"New passwords don't match."))

        user = authenticate(username=data.get('username'),
                            password=data.get('old_password'))
        if not user:
            raise ValidationError(_(u"""The old password you supplied does not \
match your current."""))

        return self.cleaned_data


class EmailChangeForm(Form):
    email = EmailField(label=_(u"New e-Mail"),
        widget=TextInput(attrs={'class': 'textbox'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')

        try:
            user = User.objects.get(email=email)
            if user:
                raise ValidationError(_(u'That e-mail is already in use.'))
        except User.DoesNotExist:
            return self.cleaned_data

class UploadAvatarForm(Form):
    file = ImageField(label=_('File'))
    action = CharField(widget=HiddenInput(
        attrs={'value': 'upload', 'id': 'id_action_upload'}))

    def __init__(self, *args, **kwargs):
        if 'profile' in kwargs:
            self.profile = kwargs.get('profile')
            del kwargs['profile']
        super(UploadAvatarForm, self).__init__(*args, **kwargs)

    """
    def __init__(self, *args, **kwargs):
        import pdb
        pdb.set_trace()
        if 'profile' in kwargs:
            from django.template.defaultfilters import slugify

            self.profile = kwargs.get('profile')
            print '000000000000000000000000'
            print dir(self.visible_fields)
            self.file.upload_to = slugify(self.profile.user.username)
            del kwargs['profile']
        super(UploadAvatarForm, self).__init__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        if 'fields' not in self:
            return nada
        super(UploadAvatarForm, self).__getitem__(*args, **kwargs)
    """

    def clean_file(self):
        from profile import settings as _settings
        from profile.avatars import handle_avatar

        from utils.contenttype import is_allowed

        file = self.cleaned_data.get('file')
        if file.size > _settings.MAX_AVATAR_SIZE:
            raise ValidationError(
                _(u"File too big. The maximum size allowed is %iMB \
                    (megabytes)") % (_settings.MAX_AVATAR_SIZE / (1024^2)))
        if not is_allowed(file):
            raise ValidationError(_(u"The file type is not supported."))
        return file


class RetrieveImageForm(Form):
    url = URLField(label=_('Web address'), verify_exists=True,
        widget=TextInput(attrs={'class': 'textbox'}),
        validator_user_agent="""Mozilla/5.0 (X11; U; Linux i686) \
Gecko/20071127 Firefox/2.0.0.11""")
    action = CharField(widget=HiddenInput(
        attrs={'value': 'url', 'id': 'id_action_url'}))

    def clean_url(self):
        from utils.contenttype import is_allowed
        from mimetypes import guess_type

        url = self.cleaned_data.get('url')
        print url
        file_type = guess_type(url)
        print file_type
        if is_allowed(file_type):
            return url
        raise ValidationError(_(u"The file type is not supported."))


class ChooseWallpaperForm(Form):
    token = CharField(label=_(u"Search text"),
        widget=TextInput(attrs={'class': 'textbox'}))
    action = CharField(widget=HiddenInput(
        attrs={'value': 'wallpaper', 'id': 'id_action_wallpaper'}))


# DEPRECATED: Eliminar
class DummyAvatarForm:
    avatar = None

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            from profile.models import Avatar

            avatar_id = args[0].get('avatar')
            # Un id == 0 significa que voy a usar el default avatar.
            if avatar_id == '0':
                self.avatar = Avatar()
                self.avatar.id = 0
            else:
                try:
                    self.avatar = Avatar.objects.get(id=avatar_id)
                except Exception, e:
                    print e

    def is_valid(self):
        return type(self.avatar).__name__ == 'Avatar'


