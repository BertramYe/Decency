from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from .models import LikeCount,LikeRecord
from django.http import JsonResponse

def userliked(request):
    liked_user = request.user
    models_name =request.GET.get("model_name")
    content_type = ContentType.objects.get(model = models_name)
    object_id = request.GET.get("object_id")
    isliked = request.GET.get("is_like")
    if isliked == 'true':
        isliked = True
    else:
        isliked = False
    
    # 定义一个字典，用于返回点赞过程中，后端的反馈信息
    data = {}
    # 验证用户是否登录
    if liked_user.is_authenticated:
        data['user_login'] = True
        if isliked != True:   # 前端用户没有点赞过，此时要点赞
            # 要点赞
            # 先查一下点赞记录（没有点赞记录，就创建一条点赞记录）
            likerecords,created= LikeRecord.objects.get_or_create(content_type = content_type,object_id = int(object_id),liked_user=liked_user)
            if created:
                # 如果是创建的，说明确实未点赞过，此时要点赞，可以在LikeCount这张表里面加上一条点赞，
                # 如果本身没有对这篇文章的点赞，那就创建一条这篇文章的点赞统计
                likescount,created = LikeCount.objects.get_or_create(content_type = content_type,object_id = int(object_id))
                likescount.liked_numbers +=1
                likescount.save()
                # 并返回新的点赞数量
                data['liked_number'] = likescount.liked_numbers
                # 返回用户点赞过
                data['user_liked'] = True 
        else:
            # 否则的话，说明有记录存在，此时是为了取消点赞
            # 先查一下点赞记录
            likerecords = LikeRecord.objects.filter(content_type = content_type,object_id =int(object_id),liked_user=liked_user)
            if likerecords.exists():
                # 如果确实已经点赞过了，此时可以取消
                likescount = LikeCount.objects.get(content_type = content_type,object_id = int(object_id))
                likescount.liked_numbers -= 1
                likescount.save()
                # 保存完点赞数，将点赞记录删除
                likerecords.delete()
                # 返回新的点赞数量
                data['liked_number'] = likescount.liked_numbers
                # 返回用户没有点赞过
                data['user_liked'] = False            
    else:
        data['user_login'] = False
        # 如果用户未登录，统一返回用户没有点赞过
        data['user_liked'] = False
    return JsonResponse(data)

