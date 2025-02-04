from django.contrib import admin
from .models import Comment

# Register your models here.
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment_content', 'comment_time',
                    'object_id', 'content_type', 'content_object','root',
                    'parent','replied_user','comment_display_or_not','comment_readed_or_not')
    ordering = ('id',)

admin.site.register(Comment, CommentAdmin)
