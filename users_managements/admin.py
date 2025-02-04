from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# 导入自定义的模型
from .models import UserProfile,OAuthRelationship,OpenIDType


# 下面这两个新的类，UserProfileInline和UserAdmin是
# 为了将我们自定义的用户模型UserProfile在后台用户的认证和授权里面也能看见和操作
# Define an inline admin descriptor for UserProfile model
# which acts a bit like a singleton
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    # verbose_name_plural = 'UserProfile'

# 自定义一个新的用户后台管理模型
# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('id','username','nickname','email','is_staff','is_active','is_superuser')
    
    # 定义一个对应的自定义的方法，将nickname字段绑定到UserAdmin后台模型里面 
    # 注意这个方法一定要和 list_display 里面的属性一致，否则无法被调用
    def nickname(self,obj):
        return obj.userprofile.nickname

    # 修改 nickname 的字段描述成中文   
    nickname.short_description = '昵称'

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user','nickname')
    ordering = ('id',)

class OAuthRelationshipAdmin(admin.ModelAdmin):
    list_display=('id','user','open_id','open_id_type_index')
    ordering = ('id',)

class OpenIDTypeAdmin(admin.ModelAdmin):
    list_display=('id','open_id_type_index','open_id_type_name')
    ordering = ('id',)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 注册自定义的模型
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(OAuthRelationship,OAuthRelationshipAdmin)
admin.site.register(OpenIDType,OpenIDTypeAdmin)