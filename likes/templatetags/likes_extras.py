# 记住而在调用时先需要{% load %} 操作
from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import LikeCount,LikeRecord
from django.core.exceptions import ObjectDoesNotExist
# 注册我们自定义的函数
register = template.Library()

@register.simple_tag
def get_likes_numbers(article_id,models_name):
    # 传入具体的文章对象的主键id值，统计我们文章被点赞的总数
    try:
        content_type = ContentType.objects.get(model = models_name)
        # LikeCount.objects.filter(object_id = article_id)
        likecount = LikeCount.objects.get(object_id = article_id,content_type=content_type)
        total_liked_numbers = likecount.liked_numbers
    except ObjectDoesNotExist:
        total_liked_numbers = 0
    return total_liked_numbers


@register.simple_tag(takes_context=True)
def user_liked_or_not(context, article_id, models_name):
    # 传入具体的文章对象的主键id值,并查询用户是否点赞
    user = context['user']
    content_type = ContentType.objects.get(model = models_name)
    # takes_context = true 可以获取页面特定的键值信息
    if user.is_authenticated:
        if LikeRecord.objects.filter(object_id = int(article_id),liked_user = user,content_type=content_type).exists():
            return 'like-active'
    else:
        return ''
    