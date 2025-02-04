from comments.models import Comment
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions  import ObjectDoesNotExist
# 传入 django-ckeditor的widget模块，添加到 comment_content 模块里面
from ckeditor.widgets import CKEditorWidget

# 利用django自带的forms表单，处理留言评论功能
class CommentForm(forms.Form):

    # 定义需要传入的属性信息
    object_id_widget = forms.HiddenInput()
    content_type_widget = forms.HiddenInput()
    comment_content_widget = CKEditorWidget(config_name='comment_ckeditor_config')
    reply_comment_id_widget = forms.HiddenInput(attrs={'id':'reply_comment_id'})
    # 将需要的字段传入form表单里面
    object_id = forms.IntegerField(widget=object_id_widget)
    content_type = forms.CharField(widget=content_type_widget)
    # 下面的require字段表示必填字段
    comment_content = forms.CharField(widget=comment_content_widget,error_messages={'required':'评论内容不能为空!'})
    # 为了评论回复，需要在form表单里面传入评论的id值，为此我们可以多设置一个隐藏字段
    reply_comment_id = forms.IntegerField(widget=reply_comment_id_widget)
 

    def __init__(self,*args,**kwargs):
        # 在这里面是为了防止参数混淆，因为user我们可以直接通过request.user去获取，
        # 为了防止数据混乱，提前在实例化的时候，将user信息给剔除出去
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(CommentForm,self).__init__(*args,**kwargs)
 
    # 判断用户是否登录
    def clean(self):
        if self.user.is_authenticated:
            self.cleaned_data['user']=self.user
        else:
            raise forms.ValidationError("用户尚未登录！")

        # 验证评论的对象（文章） content_object 是否存在
        # 获取提交的object_id和content_type，从而利用这两个信息获取到我们想要的content_object
        submit_object_id = self.cleaned_data['object_id']
        submit_content_type = self.cleaned_data['content_type']
        try:    # 用 try 尝试，如果获取不到对应的评论对象，就抛异常
            content_type = ContentType.objects.all().get(model=submit_content_type) 
            # model_class()方法是将对应的content_type转化为对应的model对象
            model_article = content_type.model_class()
            # 利用获取到的article模型查询我们想要的信息
            content_object_article = model_article.objects.get(pk = submit_object_id)
            self.cleaned_data['content_object_article'] = content_object_article
        except  ObjectDoesNotExist:
            raise forms.ValidationError("评论的文章不存在，请刷新网页再试！") 
        return self.cleaned_data
    
    # 对前端传过来的reply_comment_id字段信息进行验证
    def clean_reply_comment_id(self):
        reply_comment_id = self.cleaned_data['reply_comment_id']
        if reply_comment_id <0:
            raise forms.ValidationError("回复评论出错，请刷新网页后重新尝试！")
        elif reply_comment_id==0:
            # 顶级评论，将parent字段设置为 None
            self.cleaned_data['parent'] = None
        elif Comment.objects.filter(pk = reply_comment_id).exists():
            self.cleaned_data['parent'] = Comment.objects.get(pk = reply_comment_id)
        else:
            raise forms.ValidationError("回复评论出错，请刷新网页后重新尝试！")
        return reply_comment_id



