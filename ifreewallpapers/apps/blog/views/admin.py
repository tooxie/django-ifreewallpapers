# coding=UTF-8
from blog.models import Post
from blog.forms import NewPostForm

from utils.decorators import render_response
to_response = render_response('blog/')

from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.template.defaultfilters import slugify

@to_response
def do_post(request):
    form = NewPostForm()
    if request.method == 'POST':
        post = request.POST.copy()
        form = NewPostForm(post, user=request.user)
        if form.is_valid():
            new_post = Post()
            new_post.user = request.user
            new_post.title = post.get('title')
            new_post.draft = post.get('draft', False)
            new_post.source = post.get('content')
            new_post.save()
            new_post.tags = post.get('tags', '')
            return HttpResponseRedirect(reverse('profile', 
                kwargs={'slug': request.user.get_profile().slug}))
        try:
            original_post = Post.objects.get(
                blog__owner=request.user, slug=slugify(post.get('title'))).html
        except:
            original_post = None
    return 'post.html', {'post_form': form, 'editing': True,
                         'original_post': original_post}
