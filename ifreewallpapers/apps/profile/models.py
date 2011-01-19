# coding=UTF-8
from profile.countries import CountryField
from profile import settings as _settings


from django.db.models import Model, ForeignKey, CharField, DateTimeField, \
                             DecimalField, BooleanField, TextField, URLField, \
                             PositiveIntegerField, DateField, SlugField
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


class Profile(Model):
    """A user profile."""
    user = ForeignKey(User, unique=True, verbose_name=_(u'User'),
        related_name='profile')
    slug = SlugField(_(u'Slug'))
    country = CountryField(_(u'Country'), null=True, blank=True)
    latitude = DecimalField(_(u'Latitude'), max_digits=10, decimal_places=6, blank=True,
        null=True)
    longitude = DecimalField(_(u'Longitude'), max_digits=10, decimal_places=6, blank=True,
        null=True)
    location = CharField(_(u'Location'), max_length=255, blank=True)
    # TODO:
    # TODO: Implementar fecha de nacimiento.
    birthdate = DateField(_(u'Birthdate'))
    url = URLField(_(u'Website'), verify_exists=False)
    avatar = ForeignKey('Avatar', verbose_name=_(u'Avatar'), related_name='default_for', blank=True,
        null=True)

    def save(self):
        if not self.id:
            slug = slugify(self.user.get_full_name())
            x = 0
            while Profile.objects.filter(slug=slug).count():
                slug = "%s_%i" % (slug, x)
                x += 1
            self.slug = slug
        super(Profile, self).save()

    """
    def get_current_avatar(self):
        try:
            return self.default_avatar.all()[0]
        except:
            return ''
    avatar = property(get_current_avatar)
    """

    def count_avatars(self):
        print self.avatars.all().count()
        return self.avatars.all().count()

    def has_avatar(self):
        return bool(self.count_avatars())

    def get_avatars(self):
        return self.avatars.all()

    def __unicode__(self):
        return _(u"%s's profile") % self.user

    def get_absolute_url(self):
        return reverse("profile_public", args=[self.user])

    def avatars_root(self):
        from os import path

        return path.join(_settings.AVATARS_DIR, self.slug)

    def get_groups(self):
        groups = []
        for data in self.fields.all():
            group = data.field.group
            if group not in groups:
                if group.position:
                    x = group.position
                else:
                    x = 0
                    while x < len(groups) and group.name > groups[x].name:
                        x += 1
                groups.insert(x, group)
        return groups

    def has_blog(self):
        from blog.models import Blog

        return bool(Blog.objects.filter(owner=self.user).count())

    def get_registration(self):
        return self.registration.all().order_by('-cdate')[0]


class Avatar(Model):
    """An avatar for a user."""
    profile = ForeignKey(Profile, verbose_name=_(u'Profile'), related_name='avatars')
    name = CharField(_(u'Name'), max_length=255)
    cdate = DateTimeField(_(u'Creation Date'), auto_now_add=True)

    def __unicode__(self):
        return _(u"%s's Avatar") % self.profile.user.username

    def delete(self):
        from os import path, remove

        if path.exists(self.name):
            remove(self.name)
        if self.is_default():
            profile = self.profile
            profile.avatar = None
            profile.save()
        super(Avatar, self).delete()

    def url(self):
        from profile.avatars import avatar_to_url

        return avatar_to_url(self)

    def is_default(self):
        return self.profile.avatar.id == self.id

    def save(self):
        if self.name:
            if self.name.startswith(_settings.AVATARS_DIR):
                self.name = self.name.replace(_settings.AVATARS_DIR, '')
        super(Avatar, self).save()


class FieldGroup(Model):
    """A logical group to organize fields."""
    name = CharField(_(u'Name'), max_length=255)
    position = PositiveIntegerField(_(u'Position'), blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_fields_for(self, user, empty=False):
        fields = []
        if empty:
            for field in self.fields.all():
                fields.append(field)
        else:
            for field in self.fields.filter(
                    all_data__owner=user.get_profile()):
                if field not in fields:
                    fields.append(field)
        return fields

    def get_fields_data_for(self, user, empty=False):
        fields = []
        if empty:
            for field in self.fields.all():
                for data in field.all_data.all():
                    fields.append(data)
        else:
            for field in self.fields.filter(
                    all_data__owner=user.get_profile()).order_by(
                        'position', 'name'):
                for data in field.all_data.all():
                    if data not in fields:
                        fields.append(data)
        return fields


FIELD_TYPES = (
    ('CB', _('Check Box')),
    ('IM', _('Image')),
    ('MC', _('Multiple Choices')),
    ('SC', _('Single Choice')),
    ('TB', _('Text Box')),
    ('TA', _('Text Area')))

MULTIPLE_FIELDS = ('MC', 'SC')
LONG_TEXT_FIELDS = ('TA')
SINGLE_CHOICE_FIELDS = ('SC')


class Field(Model):
    """The definition of a field. It declares the type of the field and the
    group it belongs to."""
    name = CharField(_(u'Name'), max_length=255)
    group = ForeignKey(FieldGroup, verbose_name=_(u'Group'),
        related_name='fields')
    position = PositiveIntegerField(_(u'Position'), blank=True, null=True)
    type = CharField(_(u'Type'), max_length=2, choices=FIELD_TYPES)

    def __unicode__(self):
        return _('%(name)s - %(group)s') % {'name': self.name,
                                            'group': self.group}

    def is_multiple(self):
        return self.type in MULTIPLE_FIELDS

    def is_single_choice(self):
        return self.type in SINGLE_CHOICE_FIELDS

    def is_long_text(self):
        return self.type in LONG_TEXT_FIELDS


class FieldData(Model):
    """The data for a field. Could be a string, a long text, a choice from a
    Multiple Choice field or a boolean from a Check Box field."""
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.contenttypes import generic

    field = ForeignKey(Field, verbose_name=_(u'Field'),
        related_name='all_data')
    owner = ForeignKey(Profile, verbose_name=_(u'Owner'),
        related_name='fields')
    content_type = ForeignKey(ContentType, verbose_name=_(u'Content Type'))
    object_id = PositiveIntegerField(_(u'Object ID'))
    data = generic.GenericForeignKey('content_type', 'object_id')
    public = BooleanField(_(u'Public'))

    def __unicode__(self):
        return _(u'%(field)s: %(data)s') % {'field': self.field,
                                            'data': self.data}

    def _name(self):
        return self.field.name
    name = property(_name)

    def delete(self):
        print 'deleting', str(self) + '...'
        try:
            model = self.content_type.model_class()
            if model.__name__ != 'FieldChoice':
                data = model.objects.get(id=self.object_id)
                if FieldData.objects.filter(
                        content_type=self.content_type,
                        object_id=self.object_id).count() == 1:
                    print 'deleting', str(data) + '...'
                    data.delete()
        except Exception, e:
            print 'FieldData.delete()', e
        super(FieldData, self).delete()

    class Meta:
        unique_together = ('field', 'owner', 'content_type', 'object_id')


class FieldChoice(Model):
    """A choice for Multiple Single Choice or fields. This will then be
    referenced from FieldData as a foreign key."""
    field = ForeignKey(Field, verbose_name=_(u'Field'), related_name='choices')
    choice = CharField(_(u'Choice'), max_length=255, null=False, blank=False)

    def __unicode__(self):
        return self.choice

    class Meta:
        unique_together = ('field', 'choice')


class CharData(Model):
    """A string data for a field."""
    content = CharField(_(u'Content'), max_length=255, unique=True,
        null=False, blank=False)

    def __unicode__(self):
        return self.content

    # TODO: Esta función esta hecha para evitar guardar datos duplicados y
    # TODO: reutilizar los objetos de la base. Chequear que no existan
    # TODO: efectos colaterales no deseados.
    def save(self, *args, **kwargs):
        if FieldData.objects.filter(content=self.content).count() == 1:
            object = FieldData.objects.get(content=self.content)
            self.id = object.id

        super(CharData, self).save(*args, **kwargs)


class TextData(Model):
    """A text data for a field."""
    content = TextField(_(u'Content'), unique=True, null=False, blank=False)

    def __unicode__(self):
        return self.content

class Registration(Model):
    user = ForeignKey(User, verbose_name=_(u'User'),
        related_name='registration', unique=True)
    key = CharField(_(u'Key'), max_length=32, unique=True)
    completed = BooleanField(_(u'Registration Complete'), default=False)
    cdate = DateTimeField(_(u'Creation Date'))

    def save(self):
        from datetime import datetime

        if not self.id:
            self.cdate = datetime.now()
        super(Registration, self).save()

    def get_date(self):
        return _(u'%(day)i/%(month)i/%(year)i') % \
            {'day': self.datetime.day, 'month': self.datetime.month,
             'year': self.datetime.year}

    def complete(self):
        self.user.is_active = True
        self.user.save()

        self.completed = True
        self.save()

        return True
