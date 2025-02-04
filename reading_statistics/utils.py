import datetime
from articles.models import Article
from .models import ArticleReadNumber,ArticleReadDeatil
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum


def read_number_addition(request,key):
    # 用户的阅读次数（每当用户点击进页面就会增加一次阅读量）
    # 同时利用request请求里面的 cookies，看看有没有值，如果没有值，即当前session被关闭了，
    # 那么阅读量加1，否则不加，同时，记得不能直接利用session而利用我们自定义的字段是因为，session是整个浏览器的会话
    # 用户可能在·同一个会话里面打开多个文章页面阅读，此时我们添加的cookies字段f"article_{article_id}__readed"，会随着请求的增加而增加，
    # 但是会话sessionid 永远只有一个，这样会导致阅读量的数据不准确
    cookies_value = f"article_{key}__readed"
    if not request.COOKIES.get(cookies_value):
        article_table = ContentType.objects.get_for_model(Article)
        # 每篇文章的总阅读量 +1
        # 注意这里不用创建，请因为请求时，就已经被get_read_number()函数创建过了，这里只用在请求时+1就好
        reading_articles = ArticleReadNumber.objects.get(content_type = article_table,object_id = key)
        reading_articles.read_numbers += 1
        reading_articles.save()

        # 每天的阅读量+1
        reading_date = timezone.now().date()
        # 数据不存在就创建，created 为bool 值，创建过就为true,否则就为false
        reading_article_per_day,created = ArticleReadDeatil.objects.get_or_create(content_type = article_table,object_id = key,read_date =reading_date)
        # 因为阅读量默认都为 0 故而无论是创建了记录还是没有，只要点进去阅读量就会加1
        reading_article_per_day.read_numbers_per_day += 1
        reading_article_per_day.save()

    return cookies_value

def get_weakly_read_numbers(article_table):
    get_read_number_start_date = timezone.now().date()
    # 声明一个数组用来存储时间
    specified_dates=[]
    # 申明一个数组用来存储一周七天中每天的文章阅读总量
    weakly_read_numbers = []
    # range()是左闭右开区间
    for i in range(6,-1,-1):
        get_read_number_date=get_read_number_start_date-datetime.timedelta(days=i)
        specified_date_articles = ArticleReadDeatil.objects.filter(content_type = article_table,read_date =get_read_number_date )
        # 利用django里面的聚合函数 aggregate（）方法，按组统计数据(此时用Sum，求阅读量的和)，并且返回一个字典的结果
        total_article_read_numbers_per_day = specified_date_articles.aggregate(total_read_number_per_day =Sum('read_numbers_per_day'))
        # 将每天阅读的总量和对应的日期提取出来，存到我们自定义的列表里面，如果值不存在（None）就用默认值 0 填充
        specified_dates.append(get_read_number_date.strftime('%m/%d'))  # 将时间日期格式化成字符串
        weakly_read_numbers.append(total_article_read_numbers_per_day['total_read_number_per_day'] or 0)
    # 利用元组返回日期数据
    return specified_dates,weakly_read_numbers


# 统计特定日期地热搜文章
def hot_articles_of_specified_dates(article_table,specified_dates):
    today_articles = ArticleReadDeatil.objects.filter(content_type = article_table,read_date =specified_dates).order_by('-read_numbers_per_day')
    # 取前五篇阅读量最大的文章作为热搜文章
    hot_articles = today_articles[:5]
    return hot_articles

# 统计近一周内的热门文章
def weakly_hot_articles():
    weak_during_start = timezone.now().date()-datetime.timedelta(days=7)
    # 从过去第七天开始计算，可见今天作为默认的，可以不用写出来
    # weak_during_end = timezone.now().date()
    weakly_articles = Article.objects.filter(related_to_ArticleReadDeatil__read_date__gte=weak_during_start)
    # 将这一周内的文章数量进行分组统计，value()指定按照哪个/哪些字段进行分组统计，统计完再按照倒叙排序
    weakly_hot_articles = weakly_articles.values('id','title').annotate(weakly_read_numbers = Sum('related_to_ArticleReadDeatil__read_numbers_per_day')).order_by('-weakly_read_numbers')
    return weakly_hot_articles[:5]  

def total_reading_times():
    """ 统计文章的总阅读量 """
    # 利用aggregate函数，可以统计表格里面的特定字段的数的总和,并且会返回一个字典对象
    total_articles_read_times_dict = ArticleReadNumber.objects.aggregate(total_articles_read_times = Sum('read_numbers'))
    # 并且可以通过以下方式获取对应的参数值
    # total_articles_read_times = total_articles_read_times_dict['total_articles_read_times_dict']

    # 以下统计的是所有的文章数量
    total_articles = ArticleReadNumber.objects.values('object_id').distinct().count()
   
    # 所有文章的总数
    total_articles_read_times_dict['total_articles'] = total_articles
    total_articles_and_read_times_dict = total_articles_read_times_dict
    return total_articles_and_read_times_dict
              