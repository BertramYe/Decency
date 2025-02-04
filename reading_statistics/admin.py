from django.contrib import admin
from .models import ArticleReadNumber,ArticleReadDeatil

# Register your models here.
class ArticleReadNumberAdmin(admin.ModelAdmin):
    list_display = ('id','object_id','read_numbers','content_type')
    ordering = ('object_id',)

class ArticleReadDeatilAdmin(admin.ModelAdmin):
    list_display = ('id','object_id','read_numbers_per_day','content_type','read_date')
    ordering = ('-read_date',)


admin.site.register(ArticleReadNumber, ArticleReadNumberAdmin)
admin.site.register(ArticleReadDeatil, ArticleReadDeatilAdmin)
