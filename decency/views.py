import datetime
from articles.models import Article
from django.shortcuts import render
from reading_statistics.utils import get_weakly_read_numbers,hot_articles_of_specified_dates,weakly_hot_articles,total_reading_times
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
# 导入缓存模块设置特定的字段进行数据库缓存操作
from django.core.cache import cache
from articles.utils import page_paginator
from django.db.models import Q
from . import settings

def homepage(request):
    article_table = ContentType.objects.get_for_model(Article)
    today_total_article_reading_times= get_weakly_read_numbers(article_table)[1][-1]
    # 今天热搜文章获取
    today = timezone.now().date()
    today_hot_articles = hot_articles_of_specified_dates(article_table,today)
    # 昨天热搜文章获取
    yesterday = timezone.now().date() - datetime.timedelta(days=1)
    yesterday_hot_articles = hot_articles_of_specified_dates(article_table,yesterday)
    # 近一周的热门文章
    # 利用 cache.get()方法获取近一周的 热点文章数据缓存数据
    # weaken_hot_articles = weakly_hot_articles()
    weaken_hot_articles = cache.get('weaken_hot_articles')
    if weaken_hot_articles is None:
        weaken_hot_articles = weakly_hot_articles()
        # 将重新获取的值，重新以字典的形式存储到缓存里面，有效期为3600s(1小时)
        cache.set('weaken_hot_articles',weaken_hot_articles,3600)
   
    now_date = datetime.datetime.now()
    now_year = str(now_date)[0:4]
    if now_year == '2021':
        now_year = 'now'

    # 所有文章的总阅读量
    
    total_articles_and_read_times_dict = total_reading_times()


    content = {}
   
    content['today_hot_articles']=today_hot_articles
    content['yesterday_hot_articles']= yesterday_hot_articles
    content['weaken_hot_articles']=weaken_hot_articles
    content['now_year'] = now_year
    content['total_articles'] = total_articles_and_read_times_dict['total_articles']    # 当前网站所有的文章数量
    content['total_articles_read_times'] = total_articles_and_read_times_dict['total_articles_read_times']  # 当前网站的所有的文章的总的阅读数量
    content['today_total_article_reading_times'] = today_total_article_reading_times  # 今天所有网站的文章的阅读量
    return render(request, 'homepage.html', content)

def page_search(request):
    # 通过input的name属性获取form表单里面提交的值
    search_key_words = request.GET.get("search-key","")
    context = {}
    # 新建一个空文章列表，用于存储我们检索到的文章内容
    article_list = []
    if search_key_words.strip() != "":
        search_list = search_key_words.strip()
        # 将检索的内容按空格进行拆分
        target_search_list = search_list.split(" ")
        for target_search_key in target_search_list:
            if  target_search_key.strip() != "":
                valid_target_search_key = target_search_key.strip()
                filtered_articles = Article.objects.filter( Q(title__icontains=valid_target_search_key) | Q(contents__icontains=valid_target_search_key )).order_by('-created_time')
                new_article_list = []
                for article in filtered_articles:
                    if article != "":
                        # print(article)
                        new_article_list.append(article)
                # 这里面是将搜索到的结果取并集，间接的做了时间的排序
                article_list = list(set(article_list) | set(new_article_list))
        # 下面这个是为了将我们获取的结果进行按时间倒叙进行排序，因为读者总是想获得最新的文章
        if len(article_list) >0:
            article_list.reverse()
            
    # 利用自定义的分页函数，将我们文章内容进行分页
    context = page_paginator(request,article_list,settings.NUMBERS_OF_ARTICLES_FOR_EACH_PAGE)
    
    # article_paginator = Paginator(article_list,settings.NUMBERS_OF_ARTICLES_FOR_EACH_PAGE)
    # page_number = request.GET.get('page',1)
    # articles_of_per_page = article_paginator.get_page(page_number)
    # total_pages = article_paginator.num_pages
    # page_num_list = []
    # for i in range(1,total_pages+1):
    #     page_num_list.append(i)


    context["search_key_words"] = search_key_words
    # context['articles_of_per_page'] = articles_of_per_page
    # context['page_num_list'] = page_num_list
    return render(request,'search.html',context)




# test web3d
def web_3D(request):
    return render(request,"stl_conbainer.html")