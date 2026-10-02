from django.contrib import admin
from .models import Profile, Post, Comment, Like, Follow, ReferralClick, Notification


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'referral_code', 'location', 'created_at']
    list_filter = ['created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content', 'created_at']
    list_filter = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'content', 'created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']


@admin.register(ReferralClick)
class ReferralClickAdmin(admin.ModelAdmin):
    list_display = ['profile', 'ip_address', 'created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
