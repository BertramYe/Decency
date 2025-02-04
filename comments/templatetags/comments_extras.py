# 我们除了可以利用python进行自定义函数，进行封装
# 在django里面我们可以自定义templatetags包，
# 进行相应功能的封装，从而可以降低耦合性以及代码量

# 记住而在调用时先需要{% load %} 操作
from django import template
from comments.forms import Comment
from comments.forms  import CommentForm
from django.contrib.contenttypes.models import ContentType
# 引入点赞函数，进行点赞排序
from likes.templatetags.likes_extras import get_likes_numbers


# 注册我们自定义的函数
register = template.Library()

@register.simple_tag
def get_comment_number(article_id):
    # 传入具体的文章对象的主键id值，我们将其进行总评论数进行统计
    # comment_display_or_not字段是为了后台管理评论
    comments_numbers = Comment.objects.filter(object_id =article_id,comment_display_or_not = True).count()
    return comments_numbers


# 实例化表单时，需要像表单对应的标签传入默认的值,以字典的方式传入
# model是取出content_type对应的model
# reply_comment_id 为评论（一级）的id值，默认我们设置为0
@register.simple_tag
def get_comments_forms(article_id):
    content_type = ContentType.objects.all().get(model="article") 
    comments_forms_initial_data = {'content_type':content_type.model,'object_id':article_id,'reply_comment_id':0}
    comments_forms = CommentForm(initial=comments_forms_initial_data)
    return comments_forms

# 自定义一个按照点赞数量进行排序的函数
# 中心思想就是将评论和回复单独拿出来，按照点赞数量进行重新遍历排序回去
# def sorted_comments_with_likes_numbers(comment_set):
#     comment_list ={}
#     sorted_comments= []
#     for comment in comment_set:
#         reply_list = {}
#         sorted_replies=[]
#         likes_numbers = get_likes_numbers(comment.pk)
#         x = {comment:likes_numbers}
#         comment_list.update(x)
#         # 利用 comment.root_comment.all() 获取当前评论的所有的回复
#         for reply in comment.root_comment.all():
#             reply_like_numbers = get_likes_numbers(reply.pk)
#             y = {reply:reply_like_numbers}
#             reply_list.update(y)
#         reply_list_resort_result = sorted(reply_list.items(), key = lambda item:item[1],reverse=True)
#         for sorted_reply,reply_like_numbers in reply_list_resort_result:
#             sorted_replies.append(sorted_reply)
#         # all_replys 是我在此处自定义的一个属性值
#         comment.all_replys= sorted_replies
#     result = sorted(comment_list.items(), key = lambda item:item[1],reverse=True)
#     for cment,likes_numbers in result:
#         sorted_comments.append(cment)
#     return sorted_comments

# 以上为整个算法的详细流程，下面为我将以上代码的简化的实现
def sorted_comments_with_likes_numbers(comment_set):
    # 声明一个数组为存储排序好的comment/reply做准备
    sorted_comments= []
    # 声明一个集合，为字典排序做准备
    comment_list ={}
    for comment in comment_set:
        likes_numbers = get_likes_numbers(comment.pk,'comment')
        x = {comment:likes_numbers}
        comment_list.update(x)
    result = sorted(comment_list.items(), key = lambda item:item[1],reverse=True)
    for cment,likes_numbers in result:
        sorted_comments.append(cment)
    return sorted_comments


# 获取一级评论
@register.simple_tag
def get_primary_comments(article_id):
    # comment_display_or_not 字段是为了后台审核留言所准备的默认为False
    primary_comments = Comment.objects.filter(object_id =article_id,parent=None,comment_display_or_not = True).order_by('-comment_time')
    # 需要将评论按照点赞数进行排序，因为点赞在另外一张表里面，不能直接进行order by
    # sorted_primary_comments = sorted_comments_with_likes_numbers(primary_comments)
    sorted_primary_comments = sorted_comments_with_likes_numbers(primary_comments)
    for comment in sorted_primary_comments:
        sorted_replies = sorted_comments_with_likes_numbers(comment.root_comment.all())
        # all_replys 是我在此处自定义的一个属性值，用来存储我们整理完的当前评论的回复内容，方便前端的调用
        comment.all_replys = sorted_replies
    return sorted_primary_comments


# 获取特定用户的评论、回复
def get_comments_and_reply_with_specified_user(user,total_comment_replies):
    comments_list = []
    # 所有的正常的评论/回复
    comments = total_comment_replies.filter(parent =None)
    for comment in comments:
        if comment.content_object.author == user:
            comments_list.append(comment)
            # comment.url = comment.get_url()
    replies_list = total_comment_replies.filter(replied_user = user)
    # 自定义属性，进行数据存储
    total_comment_replies.comments_list = comments_list
    total_comment_replies.replies_list = replies_list
    return total_comment_replies



@register.simple_tag
def get_unread_comments_and_replies_numbers(unread_user):
    # 所有的未读评论/回复
    total_unread_comment_and_replies = Comment.objects.filter(comment_display_or_not = True,comment_readed_or_not = False)
    total_unread_comment_and_replies = get_comments_and_reply_with_specified_user(unread_user,total_unread_comment_and_replies)
    unread_comments_number = len(total_unread_comment_and_replies.comments_list)
    unread_replies_numbers = total_unread_comment_and_replies.replies_list.count()
    total_unread_comments_and_replies_numbers = unread_comments_number + unread_replies_numbers

    return total_unread_comments_and_replies_numbers






