from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.pagination import paginate
from .forms import PostForm, CommentForm
from .models import Group, Post, Follow

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
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()
    page_obj = paginate(
        request,
        posts,
        POSTS_PER_PAGE
    )
    context = {
        'page_obj': page_obj,
        'author': author,
        'posts_count': posts_count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count_post = post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'count_post': count_post,
        'form': form,
        'comments': comments,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
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

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница, куда будут выведены посты авторов,
    на которых подписан текущий пользователь."""
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginate(
        request,
        posts,
        POSTS_PER_PAGE
    )
    context = {
        'page_obj': page_obj,
        'no_follows': not posts.exists()
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписка на автора."""
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect('posts:profile', author)
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect('posts:profile', author)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', author)
