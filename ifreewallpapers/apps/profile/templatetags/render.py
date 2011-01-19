# coding=UTF-8
from django.template import Context, loader
from django.utils.safestring import mark_safe

def get_field_template(field=None, editable=False):
    if field:
        type = field.type
        if editable:
            return loader.get_template('profile/edit_%s_field.html' % type)
        else:
            return loader.get_template('profile/field_%s.html' % type)
    else:
        if editable:
            return loader.get_template('profile/edit_field.html')
        else:
            return loader.get_template('profile/field.html')

def render_field(field, editable, user, change=True):
    field_template = get_field_template(editable=editable)
    try:
        render_function = 'render_%(type)s' % {'type': field.type}
        field_html = globals()[render_function](field=field, user=user,
                                                editable=editable)
    except Exception, e:
        print e
        field_html = _render(field=field, editable=editable, user=user)
    context = Context({'field': field, 'changeable': change,
        'fielddata': mark_safe(field_html)})
    return field_template.render(context)

def render_MC(field, editable=False, user=None):
    html = '<ul class="choices">'
    html += _render(field=field, editable=editable, multiple=True, user=user)
    html += '</ul>'
    return html

def render_SC(field, editable=False, user=None):
    html = '<ul class="choices">'
    html += _render(field=field, editable=editable, multiple=True, user=user)
    html += '</ul>'
    return html

def _render(field, editable=False, multiple=False, user=None):
    template = get_field_template(field, editable)
    html = ''
    if editable:
        if multiple:
            for choice in field.choices.all():
                try:
                    data = field.all_data.get(object_id=choice.id, owner=user)
                except Exception, e:
                    print e
                    data = None
                html += template.render(Context(
                    {'field': field, 'data': data, 'choice': choice}))
        else:
            try:
                data = field.all_data.get(field=field, owner=user)
            except Exception, e:
                print e
                data = None
            html += template.render(Context({'field': field, 'data': data}))
    else:
        for data in field.all_data.all():
            html += template.render(Context({'field': data}))
    return html

