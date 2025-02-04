from django.contrib.auth.models import User
from django.shortcuts import render
from .models import Comment
from .forms import CommentForm
# 导入反向解析模块
from django.urls import reverse

# 导入html转换模块，用于将html文本转换成string，用于邮件发送
from django.template.loader import render_to_string

# 导入JsonResponse用于转化我们提交的评论内容转换成json格式，因为它等同于字典，所以方便ajax进行处理
from django.http import JsonResponse
# 导入邮件发送参数，进行邮件发送
from decency import settings
# 导入获取自定义函数模块
from .templatetags.comments_extras import get_comments_and_reply_with_specified_user
# 导入自定义的邮件发送模块
from decency.utils import SendEmail


# 获取留言评论信息，并进行提交动作
def comment_submission(request):
    '''
    redirections_path = request.META.get('HTTP_REFERER',reverse('homepage'))
    
    # 一些信息验证，尽量用后端做，因为前端的不可信原则，总有一些方式绕过后端进行数据欺骗和泄露
    if not request.user.is_authenticated:
        return render(request,'error.html',{'error_message':'暂未登录，登陆后方可留言评论！',"redirections_path":redirections_path})
    comment_content= request.POST.get('comment_content','').strip()  # strip()去掉字符串首尾空格
    if comment_content=="":
        return render(request,'error.html',{'error_message':'评论内容不能为空！',"redirections_path":redirections_path})
 
    # 由于前端将content_type这个input的value固定为了 article 字符串，
    # 也就是说content_type向后端传入的结果为"article"的字符串
    try:
        string_content_type = request.POST.get('content_type','')   
        object_id = int(request.POST.get('object_id',''))
        # 利用contentType这个内置的query_set里获取我们想要的content_type
        content_type = ContentType.objects.all().get(model=string_content_type) 
        # model_class()方法是将对应的content_type转化为对应的model对象
        model_article = content_type.model_class()
        # 利用获取到的article模型查询我们想要的信息
        object_article = model_article.objects.get(pk = object_id)
    except Exception:
        return render(request,'error.html',{'error_message':'评论对象不存在，请刷新后重试！',"redirections_path":redirections_path})
 
    # 实例化Conmment,即在comment这张表里面创建留言记录
    comment = Comment()
    comment.user = request.user
    comment.comment_content = comment_content
    comment.content_object = object_article
    comment.save()
    
    # 存储完留言信息后，进行重定向，返回到当前的留言页面(当前页不存在，返回首页)
    return redirect(redirections_path) 

    '''
    # 由于我在当前comments的forms.py里面提前做了验证，故而以上评论提交代码，可以做如下改写：
    # 利用POST提交的数据，直接进行实例化操作
    # 同时在实例化的时候，由于我们将 里面的user信息已经剔除掉了，此时可以在外部自定义变量的时候，
    # 利用user = request.user，将当前真正的user信息给传进来
    comments_submit_forms = CommentForm(request.POST,user = request.user) 
    # redirections_path = request.META.get('HTTP_REFERER',reverse('homepage'))
    # 定义一个data字典，用于存储评论提交的后台状态，返回前端，让ajax处理
    data={}
    if comments_submit_forms.is_valid():
        # 检查数据通过，将数据保存
        comment = Comment()
        # comment.user = request.user
        comment.user = comments_submit_forms.cleaned_data['user']
        comment.comment_content = comments_submit_forms.cleaned_data['comment_content']
        comment.content_object = comments_submit_forms.cleaned_data['content_object_article']
        # 需要存储的回复内容
        parent = comments_submit_forms.cleaned_data['parent']
        if parent is not None:
            # 只有parent字段的值为None时，才是评论，否则都是回复
            comment.parent = parent
            comment.replied_user = parent.user
            if parent.root is not None:
                comment.root=parent.root
            else:
                comment.root = parent
        comment.save()
        # 保存完，返回评论提交的页面

        
        # 当有新的评论/回复时
        # 邮件发送给管理员进行消息提醒，因为评论需要审核
        # subject = "有新的评论/回复需要审核处理"
        context_for_email={}
        # 管理员自己发送给自己，下面这一行直接注释掉即可
        # context_for_email['target_email_address'] = comment.content_object.get_user_email()
        context_for_email['comment_content']= comment.comment_content
        context_for_email['article_url'] = comment.content_object.get_article_url()
        comment_text = render_to_string('comments/email_sending_content.html',context_for_email)
        # 利用我们自定义的邮箱发送模块，来集中发送邮件，由于是独立线程，可以减少并发量 
        email_sending = SendEmail("Comment_Tips",settings.EMAIL_HOST_USER,comment_text)
        # 开启线程
        email_sending.start()

        # return redirect(redirections_path)
        # 将后台保存好的评论数据直接返回到前端页面 
        data['status'] = "SUCCESS"   # 用于提交状态标注
        # 以下为前端渲染后台数据的内容
        data['username']= comment.user.get_username_or_nickname()
        data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S') # 时间转化成字符串
        data['comment_content']= comment.comment_content
        # 为了过滤敏感信息，需要后台审核品论内容，故而需要加一个判断
        # data['comment_display_or_not']=comment.comment_display_or_not
        # 传入一个评论点赞需要的字符串变量
        data['comment_model_name'] = 'comment'
        if parent is not None:
            data['replied_user'] = comment.replied_user.get_username_or_nickname()
        else:
            data['replied_user']=""
        data['pk'] = comment.pk
        if comment.root is not None:
            data['root_pk'] = comment.root.pk
        else:
            data['root_pk'] = ""
    else:
        # 数据验证不通过，返回错误信息
        # erros = comments_submit_forms.errors.get('comment_content')
        # print(comments_submit_forms.errors)
        # return render(request,'error.html',{'error_message':erros,"redirections_path":redirections_path})
        # 提交错误，则向前端反馈错误信息
        data['status'] = "ERROR"
        data['error_message']= list(comments_submit_forms.errors.values())[0][0]
    # 此处将data字典（评论提交的成功/失败）转换成json数据给前端ajax进行处理
    return JsonResponse(data)


# 管理前台提交过来的评论和留言信息
def comment_management(request):
    redirections_path = request.GET.get('from_page',reverse('homepage'))
    total_unrealeased_commnets = Comment.objects.filter(comment_display_or_not = False)
    
    context = {}
    context['submit_released'] = '点击释放评论'
    context['submit_delete'] = '点击删除评论'
    context['form_title'] = '释放评论/删除恶评'
    context['total_unrealeased_commnets'] = total_unrealeased_commnets
    context['redirections_path'] = redirections_path
    return render(request, 'comments/comments_managements.html', context)

    
# 释放/删除审核通过的评论内容
def released_or_delete_comment(request):
    data={}
    if request.method == 'GET':
        comment_id = request.GET.get('comment_id','')
        operation_type = request.GET.get('operation_type','')
        current_user = User.objects.get(username = request.user)
        # 为了安全性，最好后台还是验证一下此时用户的登陆状态，防止恶意调用接口
        if request.user.is_authenticated and current_user.is_staff:
            if comment_id != "":
                ready_to_released_comment = Comment.objects.get(id = comment_id)
                # 释放评论
                if operation_type =='Comment_Release':
                    # 成功获取评论/回复的id值，修改是否展示评论状态
                    ready_to_released_comment.comment_display_or_not = True
                    ready_to_released_comment.save()
                    data['Status'] = 'SUCCESS-Release'
                # 删除评论
                elif operation_type =='Comment_Delete':
                    ready_to_released_comment.delete()
                    data['Status'] = 'SUCCESS-Delete'
                else:
                    data['Status'] = 'Failed-Comment-Unpass'
            else:
                data['Status'] = 'Failed-Comment-Unpass'
        else:
            data['Status'] = 'Failed-User-Unauthorized'
    return JsonResponse(data)


# 新的评论/回复向用户去提醒
def comment_reminder(request):
    # 当用户点击进来了，等价于此时前端的click事件
    if request.user.is_authenticated:
        # 所有的正常的评论/回复
        total_comment_replies = Comment.objects.filter(comment_display_or_not = True)
        # 所有的未读评论/回复
        total_unread_comment_and_replies = total_comment_replies.filter(comment_readed_or_not = False)
        # 对评论、回复针对对应的用户进行处理
        # 把未读评论变成已读评论
        unread_comments = total_unread_comment_and_replies.filter(parent =None)
        for unread_comment in unread_comments:
            if unread_comment.content_object.author == request.user:
                unread_comment.comment_readed_or_not = True 
                unread_comment.save()
        # 把未读回复变成已读回复
        unread_reply_list = total_unread_comment_and_replies.filter(replied_user = request.user)
        for unread_reply in unread_reply_list:
            unread_reply.comment_readed_or_not = True 
            unread_reply.save()
        # 返回一个所有的消息和评论的列表
        total_comment_replies = get_comments_and_reply_with_specified_user(request.user,total_comment_replies)

    # 处理和提醒用户未读消息
    context = {}
    context['form_title'] = '我的消息'
    context['total_comment_replies'] = total_comment_replies
    return render(request, 'comments/comment_reminder.html', context)