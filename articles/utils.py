from django.core.paginator import Paginator
# 分页函数
def page_paginator(request,paginated_articles,numbers_of_each_page_articles):
    # 通过get请求获取我们定义的自变量page的值，默认我们设置为 1 ，并把它定义为我们的页码数
    # page_number = request.GET.get('page', 1)
    page_number = request.GET.get('page',1)
    # 将获取的文章内容进行分页(每页2篇文章)
    article_paginator = Paginator(paginated_articles, numbers_of_each_page_articles)
    # 通过页码数 page_number,我们利用get_page()方法获取对应的页面
    articles_of_per_page = article_paginator.get_page(page_number)
    # 为了防止页码的显示过长，我们需要进行选择性的显示页码，假设只显示当前页码的前后两页
    # 1.当前页码数
    current_page_number = articles_of_per_page.number
    # 2.总页码数
    total_pages = article_paginator.num_pages
    # 3. 获取当前页码的前后两个页码列表
    new_page_range = list(range(max(current_page_number-2, 1), min(
        total_pages, current_page_number+2) + 1))
    # 在页码省略的中间加入省略号，用来提示页码的省略
    if new_page_range[0]-1 >= 2:
        new_page_range.insert(0, "...")
    if total_pages - new_page_range[-1] >= 2:
        new_page_range.append("...")
    # 在页码列表中加入首页和尾页的页码,用于首页和尾页的跳转
    if new_page_range[0] != 1:
        new_page_range.insert(0, 1)
    if new_page_range[-1] != total_pages:
        new_page_range.append(total_pages)
    # 将生成的特定字段的结果用字典存储起来，为页面渲染做准备
    content_text = {"article_list": articles_of_per_page, "article_paginator": article_paginator, "new_page_range": new_page_range}                
    return content_text