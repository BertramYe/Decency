from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType

from articles.models import Article
from .utils import get_weakly_read_numbers,total_reading_times


def reading_statistics(request):
    """ 统计文章访问量 
        这里面主要为了显示文章的累计访问数量
    """
    article_table = ContentType.objects.get_for_model(Article)
    specified_dates,weakly_read_numbers = get_weakly_read_numbers(article_table)
    
    total_articles_read_times_dict=total_reading_times()
    content = {}
    content['weakly_read_numbers'] = weakly_read_numbers
    content['specified_dates'] = specified_dates
    content['total_articles'] = total_articles_read_times_dict['total_articles']    # 当前网站所有的文章数量
    content['total_articles_read_times'] =total_articles_read_times_dict['total_articles_read_times']  # 所有文章的总阅读量
    return render(request, 'reading_statistics/reading_statistics.html', content)