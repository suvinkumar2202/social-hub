from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('register/', views.register_view, name='register'),
    path('explore/', views.explore, name='explore'),
    path('users/', views.user_list, name='user_list'),
    path('more/', views.more_page, name='more'),
    path('referrals/', views.referrals, name='referrals'),
    path('ref/<str:code>/', views.referral_track, name='referral_track'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('settings/', views.account_settings, name='account_settings'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('post/<int:pk>/like/', views.post_like, name='post_like'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
]
