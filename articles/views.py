from django.shortcuts import get_object_or_404, render
# from .models import Article,ArticleTyple,ArticleReadNumber
from .models import Article,ArticleType
from decency import settings
from django.db.models import Count
from reading_statistics import utils
# 导入自定义的分页函数
from .utils import page_paginator

# 导入过滤html的标签信息
# from django.utils.html import strip_tags

def article_list(request):
    # 筛选出不是被删除的字段，这个字段是在models里面设置的
    articles = Article.objects.filter(is_deleted=False)
    # 调用分页函数，得到我们想要的分页的特定信息
    paginator_content_text = page_paginator(request,articles,settings.NUMBERS_OF_ARTICLES_FOR_EACH_PAGE)
    '''
    # 获取文章类型  
    article_types = ArticleTyple.objects.all()
    # 根据文章类型，统计对应的文章的数量，
    article_type_lists = []    # 创建一个空列表进行存储我们需要的信息
    for article_type in article_types:
        # 为每个特定的 article_type 创建一个属性 名叫 article_numbers，并利用filter筛选特定的article_type，并统计它的数量
        article_type.article_numbers = articles.filter(type_name = article_type).count()
        # 将新生成的类型存储在我们之前新建的列表里面，为渲染做准备
        article_type_lists.append(article_type)
    # 除了用以上的方法，还可以利用aggregate和annotate方法，这两个方法不会向上面filter那样的获取，
    # 普通的get会直接将数据从数据库读取后存储在内存，而aggregate和annotate只是在需要时才会从数据库读取数据
    aggregate（）直接统计某组指定字段的聚合结果（返回一个字典对象）
    annotate() 相当于（先分组groupby ,再类分组做统计，统计完了再返回一个字典对象，而字典里面的item的key我们可以自定义）
    如下面 默认会返回一个 {'article__count'：number},此时我们将 article__count 替换成了 article_numbers
    至此上面代码可以如下一行搞定
    '''
    # 按照 article_type 分组，再统计每组结果，返回一个字典，并把对应的值赋给 article_numbers 键
    article_type_lists = ArticleType.objects.annotate(article_numbers = Count('article'))   
    # 获取文章的年月时间
    article_dates = articles.dates("created_time","month",order='DESC')   
    # 统计特定年月的文章的数量
    article_with_date ={}
    for article_date in article_dates:
        articles_count = articles.filter(created_time__year=article_date.year,created_time__month=article_date.month).count()
        article_with_date[article_date]= articles_count
    # 利用分页函数返回的字典，我们借助这个字典进行信息追加，以减少内存消耗
    paginator_content_text["article_types"] = article_type_lists
    paginator_content_text["article_with_date"] = article_with_date
    
    # 下面这一步是在文章对象 article 中我们新增了一个属性 shortern_article ，
    # 这个属性是为了将article中原本包含的html的标签以及换行符&nbsp;去除掉，
    # 方便前端截取文章部分内容，并显示文章部分内容的提示
    # for article in paginator_content_text['article_list']:
    #     shortern_article =  strip_tags(article.contents).replace("&nbsp;","")
    #     print(shortern_article)
    #     article.shortern_article = shortern_article
    
    # 渲染特定的信息内容
    return render(request, 'articles/article_lists.html', paginator_content_text)

 
def article_details(request, article_id):
    article_details = get_object_or_404(Article,id=article_id)
    cookies_value = utils.read_number_addition(request,article_id)
    # 利用filter()方法，结合created_time字段，获取上一篇和下一篇文章，从而制作上下文章跳转功能
    # 上一篇文章
    previous_article = Article.objects.filter(
        created_time__gt=article_details.created_time).last()
    # 下一篇文章
    next_article = Article.objects.filter(
        created_time__lt=article_details.created_time).first()
    # 利用request请求内包含的用户信息，传递给前端页面，进行用户登陆验证
    # username = request.user
    # "username":username
    # 传入弹窗的form表单
    # userloginform = UserLoginForm()
    content_text = {"article_detail": article_details,
                    "previous_article": previous_article, 
                    "next_article": next_article}
    # 将响应的内容用一个字典存储起来 response 是django 内部存储的自定义的字典变量，用来存储前端的响应内容                
    response= render(request, 'articles/article_details.html', content_text) 
    # 设置浏览器的cookie的值，分别是 Name ,value(这里设为true代表已经读过了),max_age有效期（秒），expires过期时间（秒）
    # 一般max_age和 expires不设置，默认表示浏览器不关那么就一直有效
    response.set_cookie(cookies_value,'true')
    return response
    # return render(request,'articles/article_details.html', content_text)


def articles_with_type(request, articles_type):
    # 获取所有的未被删除的文章信息
    articles = Article.objects.filter(is_deleted=False)
    specified_type_name = get_object_or_404(
        ArticleType, type_name=articles_type)
    # 注意此处不能用 get获取，因为 get得到的类型不是 iterable的，而filter得到的是一个iteration
    # 这里的条件字段type_name指的是模型中的条件字段，相当于 select * from article where type_name = 'specified_type_name'
    specified_article = Article.objects.filter(
        type_name=specified_type_name, is_deleted=False)  
    # 按照 article_type 分组，再统计每组结果，返回一个字典，并把对应的值赋给 article_numbers 键
    article_type_lists = ArticleType.objects.annotate(article_numbers = Count('article')) 
    # 同样设置对应的页码数，由于articles_with_type.html这个页面继承了article_list.html
    # 故而不用再在对应的html页面内再写一遍。对应的html语句，只需在views的视图函数里面做修改即可
    # 将获取的文章进行分页(每页7篇文章)
    paginator_content_text = page_paginator(request,specified_article,settings.NUMBERS_OF_ARTICLES_FOR_EACH_PAGE)
    # 获取特定时间的文章时间
    article_dates = articles.dates("created_time","month",order='DESC')
    # 统计特定年月的文章的数量
    article_with_date ={}
    for article_date in article_dates:
        articles_count = articles.filter(created_time__year=article_date.year,created_time__month=article_date.month).count()
        article_with_date[article_date]= articles_count
    # 利用分页函数返回的字典，我们借助这个字典进行信息追加，以减少内存消耗
    paginator_content_text["type_name"]=articles_type
    paginator_content_text["article_types"]=article_type_lists
    paginator_content_text["article_with_date"]=article_with_date
    return render(request, 'articles/articles_with_type.html', paginator_content_text)

def article_with_date(request,year,month):
    # 获取全部未删除的文章
    articles = Article.objects.filter(is_deleted=False)
    # 获取特定年月的文章
    specified_article = Article.objects.filter(created_time__year=year,created_time__month = month)
    # dates() 方法可以像前端传入时间数据
    article_dates = articles.dates("created_time","month",order='DESC')
    # article_date=f"{year}年{month}月"
    # 按照 article_type 分组，再统计每组结果，返回一个字典，并把对应的值赋给 article_numbers 键
    article_type_lists = ArticleType.objects.annotate(article_numbers = Count('article')) 
    # 将获取到的特定年月的文章进行分页
    paginator_content_text = page_paginator(request,specified_article,settings.NUMBERS_OF_ARTICLES_FOR_EACH_PAGE) 
    # 统计特定年月的文章的数量
    article_with_date ={}
    for article_date in article_dates:
        articles_count = articles.filter(created_time__year=article_date.year,created_time__month=article_date.month).count()
        article_with_date[article_date]= articles_count
    # 利用分页函数返回的字典，我们借助这个字典进行信息追加，以减少内存消耗
    paginator_content_text["article_types"]=article_type_lists
    paginator_content_text["article_dates"]=article_dates
    paginator_content_text["article_date"] = article_date
    paginator_content_text["article_with_date"] = article_with_date
    return render(request, 'articles/articles_with_date.html', paginator_content_text)