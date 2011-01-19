# coding=UTF-8
from django.db import models
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _
from menuse.utils import replace_link
from django.contrib import admin

# Create your models here.
class Link(models.Model):
    nombre = models.CharField(_(u'Nombre'), max_length=100)
    pagina = models.ForeignKey(FlatPage, blank=True, null=True,
        help_text=_(u'Puede elegir una página ya creada para que el link apunte a ella.'))
    url = models.CharField(_(u'dirección'), max_length=255,
        help_text=_(u'También puede apuntar a un sitio en Internet, por ej "http://www.brasil.gov.br/" o dentro del sitio, por ej "/usuario/129/".'), blank=True)
#    padre = models.ForeignKey('Link', null=True, blank=True,
#        help_text=_(u'Si elige otro link en esta lista, este item del menú se mostrará como un subitem del elegido.'))
    posicion = models.PositiveIntegerField(_(u'posición en lista'), default=1)
    mostrar_solo_en = models.CharField(_(u'Mostrar solo en'), max_length=255, blank=True,
        help_text=_(u'Solo mostrar este link en esta dirección.'))
    no_mostrar_en = models.CharField(_(u'No mostrar en'), max_length=255, blank=True,
        help_text=_(u'No mostrar este link cuando se visite esta dirección.'))
    solo_anonimos = models.BooleanField(_(u'¿Solo usuarios anónimos?'),
        help_text=_(u'Esta opción permite que el link no sea visible una vez que le usuario se identifique ante el sistema.'))
    solo_logueados = models.BooleanField(_(u'¿Solo usuarios logueados?'),
        help_text=_(u'Si marca este campo el link solo será visible para usuarios logueados.'))
    solo_staff = models.BooleanField(_(u'¿Solo Staff?'),
        help_text=_(u'Marque este campo para que este link solo sea visible para administradores del sistema.'))
    desactivar = models.BooleanField(_(u'¿Desactivar?'),
        help_text=_(u'Si desactiva un link no se mostrará en el menú pero no será borrado.'))

    def __unicode__(self):
        mods = ''
        if self.solo_logueados:
            mods+=' (L'
        if self.solo_anonimos:
            if mods == '':
                mods=' ('
            else:
                mods+=','
            mods+='A'
        if self.solo_staff:
            if mods == '':
                mods=' ('
            else:
                mods+=','
            mods+='S'
        if mods != '':
            mods+=')'

        return self.nombre + mods

    def get_href(self, request):
        try:
            if self.pagina:
                return self.pagina.url
            elif self.url:
                return replace_link(self.url, request)
            else:
                return ""
        except Exception, e:
            return ''

    def get_allowed_url(self, request):
        return replace_link(self.mostrar_solo_en, request)

    def get_not_allowed_url(self, request):
        return replace_link(self.no_mostrar_en, request)

    class Meta:
        ordering = ('posicion','nombre')

    try:
        import admin.site.register
        admin.site.register(Link)
    except:
        class Admin:
            list_filter = ('nombre',)
            search_fields = ('nombre', 'pagina', 'url')

class Menu(models.Model):
    nombre = models.CharField(_(u'nombre'), max_length=100)
    descripcion = models.TextField(_(u'descripción'), blank=True)
    mostrar_solo_en = models.CharField(_(u'Mostrar solo en'), max_length=255, blank=True,
        help_text=_(u'Solo mostrar este menú en esta dirección.'))
    no_mostrar_en = models.CharField(_(u'No mostrar en'), max_length=255, blank=True,
        help_text=_(u'No mostrar este menú cuando se visite esta dirección.'))
    solo_anonimos = models.BooleanField(_(u'¿Solo usuarios anónimos?'),
        help_text=_(u'Esta opción permite que el menú no sea visible una vez que le usuario se identifique ante el sistema.'))
    solo_logueados = models.BooleanField(_(u'¿Solo usuarios logueados?'),
        help_text=_(u'Si marca este campo el menú solo será visible para usuarios logueados.'))
    solo_staff = models.BooleanField(_(u'¿Solo Staff?'),
        help_text=_(u'Marque este campo para que este menú solo sea visible para administradores del sistema.'))
    links = models.ManyToManyField(Link, blank=True)

    def __unicode__(self):
        return self.nombre

    def get_allowed_url(self, request):
        return replace_link(self.mostrar_solo_en, request)

    def get_not_allowed_url(self, request):
        return replace_link(self.no_mostrar_en, request)

    class Meta:
        verbose_name = _(u'menu')
        verbose_name_plural = _(u'menues')
        ordering = ('nombre',)

    try:
        import admin.site.register
        admin.site.register(Link)
    except:
        class Admin:
            list_filter = ('nombre',)
            search_fields = ('nombre','descripcion')

admin.site.register(Link)
admin.site.register(Menu)
