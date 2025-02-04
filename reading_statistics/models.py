from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import DateField
from django.utils import timezone
# from django.db.models.fields import exceptions
# Create your models here.

# 将文章阅读的数量的统计独立出来，这样在我们修改原文章内容时，不会影响当前这个统计的数据
# 间接利用ContentType这个model，它相当于中介，可以帮助我们在不同的app里面的model相连接起来
class ArticleReadNumber(models.Model):
    # 被阅读的次数
    read_numbers = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

class ArticleReadNumberExpection():
    def get_read_number(self):
        # 做每篇文章的总数据的请求，如果在请求时，没有文章阅读量的数据，就创建一条，read_numbers默认为0
        article_table = ContentType.objects.get_for_model(self)
        reading_article,created = ArticleReadNumber.objects.get_or_create(content_type = article_table,object_id = self.pk)    
        return reading_article.read_numbers

# 新建一个模型 专门用于 文章阅读量的统计
class ArticleReadDeatil(models.Model):
    # 这个read_date代表阅读的时间
    read_date = DateField(default=timezone.now)
    read_numbers_per_day = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')



