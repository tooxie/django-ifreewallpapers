# -*- coding: utf-8 -*-
from django.template import Library, Node, TemplateSyntaxError
from django.template.defaultfilters import slugify
from menuse.models import Menu, Link
from string import lower
# from logging import _log as _

register = Library()

class MenuNode(Node):
    def __init__(self, menu_name, separator=None):
        self.menu_name = menu_name
        if separator:
            self.separator = ' ' + separator + ' '
        else:
            self.separator = ''

    def print_link(self, menu, link):
        from django.template.defaultfilters import slugify

        request = self.context['request']
        html_link = ''
        try:
            html_link = '<li class="%(class)s_link"><a href="%(href)s" \
                         title="%(title)s">%(text)s</a>%(separator)s</li>' % \
                            {'class': slugify(menu.nombre),
                             'href': link.get_href(request),
                             'title': link.nombre, 'text': link.nombre,
                             'separator': self.separator}
        except Exception, e:
            pass
        return html_link

    def can_print_here(self, object):
        not_allowed_url = object.get_not_allowed_url
        allowed_url = object.get_allowed_url
        request = self.context['request']
        if object.no_mostrar_en:
            if request.META.get('PATH_INFO') == not_allowed_url(request):
                return False
        if object.mostrar_solo_en:
            if request.META.get('PATH_INFO') != allowed_url(request):
                return False
        return True

    def can_print(self, object):
        user = self.context['user']
        if object.solo_staff:
            if not user.is_staff:
                return False
        if object.solo_logueados:
            if not user.is_authenticated():
                return False
        if object.solo_anonimos:
            if user.is_authenticated():
                return False
        return True

    def render(self, context):
        self.context = context
        html = ''
        try:
            menu = Menu.objects.get(nombre=self.menu_name)
        except:
            menu = None
        if menu:
            if self.can_print_here(menu):
                if self.can_print(menu):
                    for link in menu.links.all():
                        if self.can_print_here(link):
                            try:
                                if self.can_print(link):
                                    html += self.print_link(menu, link)
                            except Exception, e:
                                # _('render(): %s' % e)
                                pass
        return '<ul class="%(class)s">%(items)s</ul>' % \
            {'class': slugify(self.menu_name), 'items': html}

def render_menu(parser, token):
    bits = token.contents.split()
    if len(bits) == 1:
        raise TemplateSyntaxError, "render_menu recibe un argumento, el \
                                    nombre del menu. Puede contener espacios."
    menu_name = token.contents[12:]
    separator = ''
    if menu_name.find('separator=') != -1:
        menu_name, separator = token.contents[12:].split('separator=')
        if separator == '':
            raise TemplateSyntaxError, "No hay separador para render_menu."

    return MenuNode(menu_name, separator)

menu = register.tag(render_menu)
