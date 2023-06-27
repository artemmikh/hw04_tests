from core.pagination import paginate
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post

User = get_user_model()
POSTS_PER_PAGE = settings.POSTS_PER_PAGE


def index(request):
    post_list = Post.objects.all()
    page_obj = paginate(
        request,
        post_list,
        POSTS_PER_PAGE
    )
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginate(
        request,
        post_list,
        POSTS_PER_PAGE
    )
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    posts_count = posts.count()
    page_obj = paginate(
        request,
        posts,
        POSTS_PER_PAGE
    )
    context = {
        'page_obj': page_obj,
        'author': author,
        'posts_count': posts_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    count_post = post.author.posts.count()
    context = {
        'post_pk': post,
        'count_post': count_post,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):

    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'posts/post_create.html', context)
