from django.db import models
from django.contrib.auth.models import User

# 定义一个类用于记录open_id的类型
class OpenIDType(models.Model):
    # 用独立的表关联到用户登录的关系表，
    # 为以后的微信登录，新浪登录等等第三方登录接口做准备，
    # 减少对DB表结构的修改
    # 用int类型标注open_id的type类型，这样就可以在一定程度上减少错误，比如0表示QQ登录等等
    # 也有用choice来定义写死下拉参数，但是感觉从长远来看，并不推荐

    # 因为open_id_type_index被外键关联，故而需要将其设为unique
    open_id_type_index = models.IntegerField(unique=True)
    open_id_type_name = models.CharField(max_length=10)
    # 这个string会在实例化时返回我们想要的字符类型，并在adin后台显示
    def __str__(self):
        return f" <OpenIDType: {self.open_id_type_index} >"



# 定义一个新的模型用于记录用户的登陆模型
class OAuthRelationship(models.Model):
    # 利用外键关联到用户模型
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    open_id = models.CharField(max_length=500)
    # 利用 to_field 字段可以指定对应的外键对象
    open_id_type_index = models.ForeignKey(OpenIDType,on_delete=models.CASCADE,to_field='open_id_type_index')

    #定义一个字符串返回函数，用于展示
    def __str__(self):
        return f"<OAuthRelationship: {self.user}>"





    
# 新建一个用户模型，继承原有的User模型，并在新的模型里面添加我们想要的字段信息
class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20)
    def __str__(self):
        return f"<UserProfile: {self.nickname} standsfor {self.user.username} >"

# 给User这个类模块进行动态绑定方法，用于username 和 nickname的获取和渲染
def get_username_or_nickname(self):  # self 代表User类
    # 如果UserProfile里面能查到信息，就直接返回nickname信息，否则就直接返回用户注册的用户名
    if UserProfile.objects.filter(user = self).exists():
        userprofile = UserProfile.objects.get(user = self)
        return userprofile.nickname
    else:
        return self.username

# 将上面自定义的方法绑定给User模块
User.get_username_or_nickname = get_username_or_nickname









