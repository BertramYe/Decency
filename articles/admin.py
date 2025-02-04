from django.contrib import admin
# from .models import Article, ArticleTyple,ArticleReadNumber
from .models import Article, ArticleType


class ArticleAdimin(admin.ModelAdmin):
    # 下面read_number调用的是Article类内的read_number这个方法,它返回self.articlereadnumber.read_numbers
    # 即Article()实例化后，假设为article,那么它返回的就是article.articlereadnumber.read_numbers,进而可调
    # ArticleReadNumber这个类里面的 read_numbers 这个字段的结果值
    # list_display = ('id', 'title', 'author', 'shorten_contents',
    #                 'created_time', 'last_update_time', 'is_deleted','get_read_number')
    list_display = ('id', 'title', 'author', 'shorten_contents',
                    'created_time', 'last_update_time', 'is_deleted','get_read_number')
    ordering = ('id',)

# Register your models here.


class ArticleTypleAdimin(admin.ModelAdmin):
    list_display = ('id', 'type_name')
    ordering = ('id',)
'''
class ArticleReadNumberAdmin(admin.ModelAdmin):
    list_display = ('id', 'article','read_numbers')
    ordering = ('id',)

'''

admin.site.register(Article, ArticleAdimin)
admin.site.register(ArticleType, ArticleTypleAdimin)
# admin.site.register(ArticleReadNumber, ArticleReadNumberAdmin)
