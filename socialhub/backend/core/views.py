from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count
from .models import Profile, Post, Comment, Like, Follow, ReferralClick, Notification
from .forms import (
    UserRegisterForm, PostForm, CommentForm,
    UserUpdateForm, ProfileUpdateForm,
)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    ref_code = request.GET.get('ref', '')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = UserRegisterForm(initial={'referral_code': ref_code})
    return render(request, 'core/register.html', {'form': form, 'ref_code': ref_code})


@login_required
def feed(request):
    following_ids = request.user.following.values_list('following_id', flat=True)
    posts = Post.objects.filter(author_id__in=list(following_ids) + [request.user.id])
    post_form = PostForm()
    comment_form = CommentForm()
    return render(request, 'core/feed.html', {
        'posts': posts,
        'post_form': post_form,
        'comment_form': comment_form,
    })


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'post_id': post.id})
            return redirect('feed')
    return redirect('feed')


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('feed')
    return redirect('feed')


@login_required
@require_POST
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                post=post,
            )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': post.like_count(),
        })
    return redirect('feed')


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(
            follower=request.user, following=user
        ).exists()
    return render(request, 'core/profile.html', {
        'profile_user': user,
        'posts': posts,
        'is_following': is_following,
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'core/profile_edit.html', {
        'u_form': u_form,
        'p_form': p_form,
    })


@login_required
@require_POST
def follow_toggle(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if request.user == user_to_follow:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    follow, created = Follow.objects.get_or_create(
        follower=request.user, following=user_to_follow
    )
    if not created:
        follow.delete()
        following = False
    else:
        following = True
        if user_to_follow != request.user:
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow',
            )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'following': following,
            'follower_count': user_to_follow.profile.follower_count(),
        })
    return redirect('profile', username=username)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='comment',
                    post=post,
                )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'username': comment.author.username,
                    'content': comment.content,
                    'comment_count': post.comment_count(),
                })
            return redirect('feed')
    return redirect('feed')


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_id = comment.post.id
    comment.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post = Post.objects.get(pk=post_id)
        return JsonResponse({
            'success': True,
            'comment_count': post.comment_count(),
        })
    return redirect('feed')


def explore(request):
    posts = Post.objects.all()[:50]
    users = User.objects.all()[:20]
    return render(request, 'core/explore.html', {'posts': posts, 'users': users})


@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'core/user_list.html', {'users': users})


@login_required
def more_page(request):
    return render(request, 'core/more.html')


@login_required
def referrals(request):
    profile = request.user.profile
    referral_link = request.build_absolute_uri(f'/register/?ref={profile.referral_code}')
    total_referrals = profile.referral_count()
    recent_clicks = profile.referral_clicks.all()[:10]
    return render(request, 'core/referrals.html', {
        'referral_link': referral_link,
        'referral_code': profile.referral_code,
        'total_referrals': total_referrals,
        'recent_clicks': recent_clicks,
    })


def referral_track(request, code):
    try:
        profile = Profile.objects.get(referral_code=code)
        ReferralClick.objects.create(
            profile=profile,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
    except Profile.DoesNotExist:
        pass
    return redirect('register', ref=code)


@login_required
def notifications(request):
    notifs = request.user.notifications.all()[:30]
    unread_count = request.user.notifications.filter(is_read=False).count()
    return render(request, 'core/notifications.html', {
        'notifications': notifs,
        'unread_count': unread_count,
    })


@login_required
@require_POST
def mark_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('notifications')


@login_required
def account_settings(request):
    return render(request, 'core/account_settings.html')


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')
