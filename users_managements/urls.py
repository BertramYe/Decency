from django.urls import path

from . import views


urlpatterns = [
    path('login/',views.userlogin,name='userlogin'),
    path('login_with_qq',views.login_with_qq,name='login_with_qq'), # 用户用QQ登录
    path('user_login_modal/',views.user_login_model,name='user_login_model'),# 登录小弹窗的验证模块
    path('register/',views.userregister,name='userregister'),  # 用户注册
    path('login_out/',views.userloginout,name='userloginout'), # 用户登出
    path('userinformation/',views.userinformation,name='userinformation'), # 用户信息  
    path('change_user_information/change_nickname/',views.change_nickname,name='change_nickname'), # 修改用户信息---昵称修改
    path('change_user_information/bind_email/',views.bind_email,name='bind_email'), # 修改用户信息---绑定/修改邮箱地址
    path('change_user_information/send_email_with_verify_code/',views.send_email_with_verify_code,name='send_email_with_verify_code'), # 修改用户信息---发送邮箱验证码
    path('change_user_information/change_password/',views.change_password,name='change_password'), # 修改密码
    path('change_user_information/bind_qq/',views.bind_qq,name='bind_qq'), # 绑定QQ
]