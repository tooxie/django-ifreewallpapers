# coding=UTF-8
from blog.models import Post
from blog.forms import NewPostForm

from django.template import Library, Node, Template, TemplateSyntaxError, \
    Variable, loader, Context
from django.utils.translation import ugettext as _

# from django.conf import settings

register = Library()
DEFAULT_NUM_ENTRIES = 5

def get_user(varname, context):
    return Variable(varname).resolve(context)

class BlogPostNode(Node):
    def __init__(self, user, entries):
        self.entries = entries
        self.user = user

    def get_num_entries(self, context):
        try:
            entries = int(self.entries)
        except:
            entries = Variable(self.entries).resolve(context)
        return entries

    def get_posts(self, user, how_many):
        return Post.objects.filter(
            blog__owner=user, status=Post.PUBLISHED).order_by(
                '-cdate', 'slug')[:how_many]

    def render(self, context):
        how_many = self.get_num_entries(context)
        user = get_user(self.user, context)
        html = ''
        post_template = loader.get_template('blog/post_short.html')
        for post in self.get_posts(user, how_many):
            html += post_template.render(Context({'post': post}))
        if not html:
            html = _(u"The user hasn't posted anything yet.")
        return html


class BlogPostFormNode(Node):
    def __init__(self, user):
        self.user = user

    def is_owner(self, user, context):
        visitor = Variable('user').resolve(context)
        if visitor.is_authenticated():
            return visitor.id == user.id
        return False

    def render(self, context):
        user = get_user(self.user, context)
        if self.is_owner(user, context):
            post_form = NewPostForm()
            html = loader.get_template(
                'blog/form.html').render(
                    Context(
                        {'user': user, 'post_form': post_form}))
        else:
            html = ''
        return html


@register.tag('latest_blog_entries')
def blog_post(parser, token):
    how_many_entries = DEFAULT_NUM_ENTRIES
    bits = token.contents.split()
    if len(bits) == 1:
        raise TemplateSyntaxError(_(u"Not enough arguments for \
latest_blog_entries. You need to specify at least a user."))
    elif len(bits) == 2:
        user = bits[1]
    elif len(bits) == 3:
        user = bits[1]
        how_many_entries = bits[2]
    elif len(bits) > 3:
        raise TemplateSyntaxError(_(u"Too many arguments for \
latest_blog_entries"))
    return BlogPostNode(user, how_many_entries)

@register.tag('blog_post_form')
def blog_post_form(parser, token):
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError(_(u"Arguments error: Please specify only \
the user."))
    return BlogPostFormNode(bits[1])
