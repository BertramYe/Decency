from django.urls import path
from . import views


urlpatterns = [
    path('comment_submission', views.comment_submission, name='comment_submission'),
    path('comment_management', views.comment_management, name='comment_management'), 
    path('comment_management/released_comment', views.released_or_delete_comment, name='released_comment'),
    path('comment_management/comment_reminder', views.comment_reminder, name='comment_reminder'),
]