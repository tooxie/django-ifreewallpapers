# coding=UTF-8
from profile.models import CharData
from profile.templatetags.render import render_field

from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe as safe
from django.template import Library, Node, Context, TemplateSyntaxError, \
                            Variable, loader
register = Library()

class ProfileFieldNode(Node):
    def __init__(self, user=None, editable=False):
        self.editable = editable
        self.change = True
        if editable:
            self.empty = True
        else:
            self.empty = False
        if user:
            self.empty = False
            self.change = False
            self.user = user
        else:
            self.user = 'user'

    def render(self, context):
        user = Variable(self.user).resolve(context)
        profile = user.get_profile()
        html = ''
        group_template = loader.get_template('profile/group.html')
        for group in profile.get_groups():
            fields_html = ''
            """
            import pdb
            pdb.set_trace()
            """
            for field in group.get_fields_for(user, empty=self.empty):
                fields_html += render_field(field, self.editable, user,
                                            self.change)
            group_context = Context({'legend': group.name,
                                     'fields': safe(fields_html)})
            html += group_template.render(group_context)
        return html
        # --- Borrar de acá en más --- #
        """
                data_html = ''
                data_count = field.all_data.count()
                if data_count > 1: # Multiple or Single Choices
                    data_html += '<ul class="choices">'

                field_template = self.get_field_template()
                data_template = self.get_field_template(field.type)
                for data in field.all_data.all():
                    # print '***', data, '***'
                    data_context = Context({'name': slugify(data.name),
                                            'data': data.data})
                    data_html += data_template.render(data_context)
                if data_count > 1: # Multiple or Single Choices
                    data_html += '</ul>'
                fields_html += field_template.render(
                    Context({'name': field.name, 'fielddata': safe(data_html)}))
            group_context = Context({'legend': group.name,
                                     'fields': safe(fields_html)})
            html += group_template.render(group_context)
        return safe(html)
        """
        # --- -------------------- --- #

@register.tag('render_fields')
def Fields(parser, token):
    bits = token.contents.split()
    user = None
    if len(bits) > 2:
        raise TemplateSyntaxError, _(u"Too many arguments.")
    if len(bits) == 2:
        user = bits[1]
    return ProfileFieldNode(user=user)

@register.tag('render_editable_fields')
def Fields(parser, token):
    bits = token.contents.split()
    if len(bits) > 1:
        raise TemplateSyntaxError, _(u"render_editable_fields require no arguments.")
    return ProfileFieldNode(editable=True)
