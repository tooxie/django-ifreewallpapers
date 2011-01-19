# coding=UTF-8
from blog.models import Blog, Post

from utils.decorators import render_response
to_response = render_response('blog/')

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

@to_response
def index(request, username):
    user = get_object_or_404(User, username=username)
    blog = Blog.objects.get(owner=user)
    return 'blog.html', {'posts': blog.posts.all()}

@to_response
def view_post(request, username, slug):
    blog_post = get_object_or_404(
        Post, blog__owner__username=username, slug=slug)
    return 'post.html', {'post': blog_post}
