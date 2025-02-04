from django.db import models
from reading_statistics.models import ArticleReadNumberExpection
from django.utils import timezone
# from ckeditor.fields import RichTextField   # 只能上传纯文本
from ckeditor_uploader.fields import RichTextUploadingField  # 可以上传文件，图片等
# 导入reverse，可以反向解析路由信息
from django.urls import reverse

# 引入内置的用户模型
from django.contrib.auth.models import User

# 设置一个通用的内置关系，将Article这个模型关联到ArticleReadDeatil这个模型里面，从而可以进行特定信息查询
# 另外注意两个不同的App间内的model，不能直接用外键关系进行查询GenericRelation相当于建立了一个新的虚拟的表
from django.contrib.contenttypes.fields import GenericRelation
from reading_statistics.models import ArticleReadDeatil


class ArticleType(models.Model):
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return self.type_name


class Article(models.Model,ArticleReadNumberExpection):
    title = models.CharField(max_length=100)
    # contents = models.TextField()
    # 调用富文本django-editor编辑器
    # contents = RichTextField() 
    contents = RichTextUploadingField()  
    created_time = models.DateTimeField(default=timezone.now)
    # auto now 表示每当我们编辑内容后，它自动会将这里面内部的时间信息替换为我们当前时间
    last_update_time = models.DateTimeField(auto_now=True)
    # 外键关联表，这里面我关联一个作者信息表，而这个表可以自建，
    # 或者我们关联我们的内部表User，这样会节省很多事情
    # models.CASCADE 表示父表删除，子表不做任何操作
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    # 被阅读的次数
    # read_numbers = models.IntegerField(default=0)
    # is_deleted用来标识文章是否被删除，默认为否
    is_deleted = models.BooleanField(default=False)
    type_name = models.ForeignKey(
        ArticleType, on_delete=models.CASCADE)
    # 利用GenericRelation将 Article这个model 和 ArticleReadDeatil连接起来，并未建立字段，
    # 相当于建立了一张第三方虚拟的表，从而将这两个model连接了起来，并且不用做migrate，虚拟的字段并非真实创建
    related_to_ArticleReadDeatil = GenericRelation(ArticleReadDeatil) 
    
    def __str__(self):
        return f"<Article:{self.title}>"  

    # 当以函数用来返回当前文章的链接地址
    # reverse可以反向解析路由的路径信息
    def get_article_url(self):
        return  reverse('article_details',kwargs={'article_id' : self.pk})

    # 返回用户的email为发送邮件提醒做准备
    def get_user_email(self):
        return self.author.email 
        
    # 定义Meta并对内容进行排序，为分页器做准备
    class Meta:
        ordering = ["-created_time"]
    # 下面函数的定义和调用是为了减少django数据后台的超长内容的显示的尴尬
    def shorten_contents(self):
        if len(str(self.contents)) >= 30:
            shorten_contents = str(self.contents)[0:30]
            return f"{shorten_contents}  ..."
        else:
            return str(self.contents)
    shorten_contents.allow_tags = True



