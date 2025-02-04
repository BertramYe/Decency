from django.contrib import admin
from .models import LikeCount,LikeRecord


class LikeCountAdmin(admin.ModelAdmin):
    list_display = ('id','object_id','liked_numbers','content_type','content_object')
    ordering = ('id',)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = ('id','object_id','liked_user','liked_times','content_type','content_object')
    ordering = ('id',)

admin.site.register(LikeCount, LikeCountAdmin)
admin.site.register(LikeRecord, LikeRecordAdmin)

