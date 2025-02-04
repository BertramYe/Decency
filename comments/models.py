from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.deletion import CASCADE


# 创建评论的模型
class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=CASCADE,related_name='comments')
    comment_content = models.TextField()
    # 评论时间自动添加
    comment_time = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType,on_delete=CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type','object_id')
    # 为了排除敏感词，我们需要加个字段进行后台审理
    comment_display_or_not = models.BooleanField(default=False)
    # 为了给与被评论/回复的对象进行消息提醒，我们需要对其进行消息提醒
    comment_readed_or_not = models.BooleanField(default=False)


    # 添加字段记录评论的回复功能(表内自连),null=True,表示当前字段可以为空
    # related_name='replies', 关联外键到对应字段，如果没有，见创建一个字段
    # 'self'表示关联到自己本身的这张表，即表内自连
    # 上一级评论内容
    parent = models.ForeignKey('self',related_name='parent_comment',null=True,on_delete=CASCADE) 
    # 被回复的用户  
    replied_user = models.ForeignKey(User,null=True,related_name='replies',on_delete=CASCADE)
    # 顶级评论
    root = models.ForeignKey('self',related_name='root_comment', null=True,on_delete=CASCADE)

    
    # __str__()方法，在实例化的时候，可以将对象转化成字符串输出
    # 这里就是将我们指定return的变量对象comment_content转化成字符串输出（parent_comment）
    def __str__(self):
        return self.comment_content

    # 评论内容按照时间由早到晚进行排序
    # 为了使回复进行正序排列，暂时将整个评论按正序排列
    class Meta:
        ordering = ["-comment_time"]
