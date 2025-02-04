from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User


class LikeCount(models.Model):
    content_type = models.ForeignKey(ContentType,on_delete=CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type','object_id')
    # 点赞的数量
    liked_numbers = models.IntegerField(default=0)


class LikeRecord(models.Model):
    content_type = models.ForeignKey(ContentType,on_delete=CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type','object_id')
    
    # 点赞的用户
    liked_user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 点赞的时间
    liked_times = models.DateTimeField(auto_now_add=True)
