from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile,OAuthRelationship
import re
from decency import settings
# 利用django自带的forms表单，设计用户登录的界面



# 以下方法是为了加载自定义的敏感字词库,并返回一个对应的正则字符串
def get_sensetive_words_string():
    target_string = ""
    senstive_file_path = settings.SENSTIVE_WORDS_LIB_PATH
    with open(senstive_file_path,"r",encoding='UTF-8') as file:
        for line in file:
            if line.strip() !="":
                target_string += ( line.strip() + "|")
    if target_string.strip() !="":
        result = "/" + target_string + "/g"
    return result


class UserLoginForm(forms.Form):
    # widget 指定表单输入的数据类型，此时指定forms.PasswordInput可以将表单内的内容显示成密文，等价于form里面的type
    # attrs 里面可以直接设置标签属性
    username_widget = forms.TextInput(
        attrs={'class': "form-control", 'placeholder': "请输入用户名或邮箱"})
    password_widget = forms.PasswordInput(
        attrs={'class': "form-control", 'placeholder': "请输入密码"})

    username_or_email = forms.CharField(label='用户名|邮箱', widget=username_widget)
    password = forms.CharField(label='密码', widget=password_widget)
    # 直接在UserLoginForm这个类里面自定义一个内置函数去做用户名和密码的验证，而不用在登录函数里面userlogin里面做验证
    # 同时验证是views里面的userlogin（）函数执行完 is_valiad()函数后，我们才能得到cleaned_data的字典，再从内去取我们想要的值
    # def verify_user_login(self):
    #     submitted_username = self.cleaned_data['username']
    #     submitted_password = self.cleaned_data['password']
    #     # 利用authenticate（）进行登录验证,authenticate()函数验证时，
    #     # 不一定要用到request参数，但是username和password是必须的
    #     user = authenticate(username =submitted_username,password=submitted_password)
    #     # 对验证结果做进一步判断，
    #     if user is None:
    #         # 验证不通过抛出异常，加入自定义的报错信息
    #         error_message = forms.ValidationError("用户名或密码错误！")
    #         self.cleaned_data['error_message'] = error_message
    #     else:
    #         # 验证通过，那么返回的user不为空，则将结果存储到cleaned_data这个字典里面，方便我们获取，和减少新字典的申明，可以极大节省内存
    #         self.cleaned_data['user'] = user
    #     return self.cleaned_data

    def clean(self):
        # 注意除了利用以上自定义的方法进行验证，还可以调用django自带的 forms 类内的clean（）方法进行验证，基本方式相同，
        # 只是减少了对错误信息的渲染，可以直接调用
        # submitted_username_or_email = self.cleaned_data['username_or_email']
        # submitted_password = self.cleaned_data['password']
        submitted_username_or_email = self.cleaned_data.get('username_or_email','').strip()
        submitted_password = self.cleaned_data.get('password','').strip()
        if submitted_username_or_email == '':
            raise forms.ValidationError('用户名不能为空！')
        if submitted_password == '':
            raise forms.ValidationError('输入的密码不能为空！')
        # 利用authenticate（）进行登录验证,authenticate()函数验证时，
        # 不一定要用到request参数，但是username和password是必须的
        user = authenticate(username=submitted_username_or_email,password=submitted_password)
        # 对验证结果做进一步判断，
        if user is None:  # 这一步代表用户并没有使用用户名登录，而是使用邮件或者其他错误的用户名
            # 如果用户名验证不通过，就用邮件尝试登录
            if User.objects.filter(email=submitted_username_or_email).exists():
                user_name = User.objects.get(email = submitted_username_or_email ).username
                user = authenticate(username=user_name,password=submitted_password)
                if user:
                    # 如果登陆成功，直接跳出函数，并指定对应的当前session的user是谁
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
                else:
                    raise forms.ValidationError("用户名或密码错误！")
            else:
                raise forms.ValidationError("用户名或密码错误！")
        else:
            # 验证通过，那么返回的user不为空，则将结果存储到cleaned_data这个字典里面，方便我们获取，和减少新字典的申明，可以极大节省内存
            self.cleaned_data['user'] = user
        return self.cleaned_data

# 设计用户注册页面
class UserRegisterForm(forms.Form):
    username_widget = forms.TextInput(attrs={'class':"form-control",'placeholder':"请输入用户名(注册后不可修改)"})
    email_widget = forms.EmailInput(attrs={'class':"form-control",'placeholder':"请输入邮箱"})
    verification_code_widget = forms.TextInput(attrs={'class':"form-control",'placeholder':"请输入邮箱收到的验证码",'style':"width:60%;float:left;margin-right:5%;"})
    verification_code_send_btn_widget = forms.TextInput(attrs={'type':'button','class':'btn btn-primary','value':'点击发送验证码'})
    password_widget = forms.PasswordInput(attrs={'class':"form-control",'placeholder':"请输入密码"})
    password_repeat_widget = forms.PasswordInput(attrs={'class':"form-control",'placeholder':"请重输一遍密码"})

    username = forms.CharField(label='用户名',min_length=3,max_length=15,widget=username_widget)
    email = forms.EmailField(label="邮箱",widget=email_widget)
    verification_code_for_register = forms.CharField(label='验证码',min_length=3,max_length=8,widget=verification_code_widget)
    verification_code_send_btn_for_register = forms.CharField(label="",required=False,widget=verification_code_send_btn_widget)
    password_for_register = forms.CharField(label='密码',min_length=6,widget=password_widget)
    password_repeatation_for_register = forms.CharField(label='密码验证',min_length=6,widget=password_repeat_widget)
    
    # 初始化类的继承
    def __init__(self,*args, **kwargs):
         # 在这里面是为了防止参数混淆，因为user我们可以直接通过request.user去获取，
        # 为了防止数据混乱，提前在实例化的时候，将user信息给剔除出去
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        self.senstive_string = get_sensetive_words_string()
        super(UserRegisterForm,self).__init__(*args,**kwargs)

    # 用户名验证
    def clean_username(self):
        submitted_username = self.cleaned_data.get('username','').strip()
        if submitted_username == "":
            raise forms.ValidationError("用户名不能为空！")
        if User.objects.filter(username = submitted_username).exists():
            raise forms.ValidationError("用户已存在，请重新输入用户名！")
        if re.search(self.senstive_string,submitted_username) != None:
            raise forms.ValidationError("该用户名不合规，请重新输入新的用户名！")
        return submitted_username
    
    # 邮箱验证
    def clean_email(self):
        submitted_email = self.cleaned_data.get('email','').strip()
        session_saved_email = self.request.session.get('target_email','')
        if submitted_email == '':
            raise forms.ValidationError('输入的邮箱地址不能为空！')
        # 注意为了安全性，最好将缓存的邮件地址与提交的那一瞬间的邮件地址做一次比较，不然会产生新的Bug
        if not(session_saved_email !="" and session_saved_email == submitted_email):
            raise forms.ValidationError("注册的邮件地址和接收验证码邮件地址不一致！")
        if User.objects.filter(email = submitted_email).exists():
            raise forms.ValidationError("该邮箱已经被注册，请重新输入一个新的邮箱！")
        return submitted_email
    
    # 对输入的验证码做一些验证
    # 下面本质上是对verification_code_send_btn进行clear验证，
    # 好处是，可以使得错误信息在verification_code_send_btn空格下面显示出来
    def clean_verification_code_for_register(self):
        verification_code_for_register = self.cleaned_data.get('verification_code_for_register','').strip()
        gen_verification_code = self.request.session.get('new_user_register','')
        if verification_code_for_register == '':
            raise forms.ValidationError("验证码不能为空！")
        # 验证验证码是否一致
        if not (verification_code_for_register !="" and gen_verification_code == verification_code_for_register):
            raise forms.ValidationError("验证码不一致，注册失败！")
        else:
            return verification_code_for_register

    # 密码验证
    def clean_password_repeatation_for_register(self):
        submitted_password_once=self.cleaned_data.get('password_for_register','').strip()
        submitted_password_second=self.cleaned_data.get('password_repeatation_for_register','').strip()
        if not ( submitted_password_second !="" and submitted_password_second == submitted_password_once):
            raise forms.ValidationError("两次输入的密码不一致，请重新输入！")
        return submitted_password_second

# 修改用户昵称
class ChangeNickNameForm(forms.Form):
    new_nickname_widget = forms.TextInput(attrs={'class':"form-control",'placeholder':"请输入新的昵称"})
    new_nickname = forms.CharField(label='新昵称',min_length=3,max_length=15,widget=new_nickname_widget)

    # 初始化类的继承
    def __init__(self,*args, **kwargs):
         # 在这里面是为了防止参数混淆，因为user我们可以直接通过request.user去获取，
        # 为了防止数据混乱，提前在实例化的时候，将user信息给剔除出去
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        self.senstive_string = get_sensetive_words_string()
        super(ChangeNickNameForm,self).__init__(*args,**kwargs)

     # 判断用户是否登录
    def clean(self):
        if self.user.is_authenticated:
            self.cleaned_data['user']=self.user
        else:
            raise forms.ValidationError("用户尚未登录！")
        # 最后返回最终验证的结果
        return self.cleaned_data
    
    # 验证传入的字段是否为空
    def clean_new_nickname(self):
        # 获取form表单里面我们想要的信息
        new_nickname = self.cleaned_data.get('new_nickname','').strip()
        # senstive_string = get_sensetive_words_string()
        # print(f"senstive_string:{senstive_string}")
        new_nickname_exist_or_not_one = UserProfile.objects.filter(nickname = new_nickname).exists()
        new_nickname_exist_or_not_two = User.objects.filter(username = new_nickname).exists()
        if new_nickname == '':
            raise forms.ValidationError('新的昵称不能为空！')
        # 这里最好加个逻辑，使得昵称不可重复
        elif new_nickname_exist_or_not_one or new_nickname_exist_or_not_two:
            raise forms.ValidationError('该昵称已存在！')
        elif re.search(self.senstive_string,new_nickname) != None:
            raise forms.ValidationError("该昵称不合规，请重新输入昵称！")    
        return new_nickname

# 修改/绑定的邮箱地址
class BindEmailForm(forms.Form):
    new_email_address_widget = forms.EmailInput(attrs={'class':"form-control",'placeholder':"请输入新的邮箱地址"})
    verification_code_widget = forms.TextInput(attrs={'class':"form-control",'placeholder':"请输入新邮箱收到的验证码"})
    verification_code_send_btn_widget = forms.TextInput(attrs={'type':'button','class':'btn btn-primary','value':'点击发送验证码'})
    
    new_email_address = forms.EmailField(label='新邮箱地址',min_length=3,max_length=30,widget=new_email_address_widget)
    verification_code_for_bind_email = forms.CharField(label='新邮箱收到的验证码',min_length=3,max_length=8,widget=verification_code_widget)
    verification_code_send_btn_for_bind_email = forms.CharField(label="",required=False,widget=verification_code_send_btn_widget)
    # 初始化类的继承
    def __init__(self,*args, **kwargs):
         # 在这里面是为了防止参数混淆，因为user我们可以直接通过request.user去获取，
        # 为了防止数据混乱，提前在实例化的时候，将user信息给剔除出去
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm,self).__init__(*args,**kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user']=self.request.user
        else:
            raise forms.ValidationError("用户尚未登录！")
        # 最后返回最终验证的结果(is_valid)
        return self.cleaned_data

    # 对输入的邮箱地址的有效性验证
    def clean_new_email_address(self):
        new_email_address = self.cleaned_data.get('new_email_address','').strip()
        if new_email_address == '':
            raise forms.ValidationError('输入的邮箱地址不能为空！')
        if User.objects.filter(email = new_email_address).exists():
            raise forms.ValidationError("该邮箱已经被绑定，不能重复绑定！")
        # 注意为了安全性，最好将缓存的邮件地址与提交的瞬间的邮件地址做一次比较，不然会产生新的Bug
        session_saved_email = self.request.session.get('target_email','')
        if not(session_saved_email !="" and session_saved_email == new_email_address):
            raise forms.ValidationError("绑定的邮件地址和接收验证码邮件地址不一致！")
        return new_email_address

    # 对输入的验证码做一些验证
    def clean_verification_code_for_bind_email(self):
        verification_code_for_bind_email = self.cleaned_data.get('verification_code_for_bind_email','').strip()
        gen_verification_code = self.request.session.get('bind_email_address','').strip()
        if verification_code_for_bind_email == '':
            raise forms.ValidationError("验证码不能为空！")
         # 验证验证码是否一致
        if not (verification_code_for_bind_email !="" and gen_verification_code == verification_code_for_bind_email):
            raise forms.ValidationError('验证码不一致，邮箱绑定失败！')
        else:
            return verification_code_for_bind_email
        
# 修改密码
class ChangePasswordForm(forms.Form):
    old_password_widget = forms.PasswordInput(attrs={'class':"form-control",'placeholder':"请输入旧密码"})
    new_password_widget = forms.PasswordInput(attrs={'class':"form-control",'placeholder':"请输入密码"})
    new_password_widget_repeat_widget = forms.PasswordInput(attrs={'class':"form-control",'placeholder':"请重输一遍新的密码"})
    
    
    old_password = forms.CharField(label='旧密码',min_length=6,widget=old_password_widget)
    new_password = forms.CharField(label='新密码',min_length=6,widget=new_password_widget)
    new_password_repeatation = forms.CharField(label='新密码验证',min_length=6,widget=new_password_widget_repeat_widget)
    
    # 初始化类的继承
    def __init__(self,*args, **kwargs):
         # 在这里面是为了防止参数混淆，因为user我们可以直接通过request.user去获取，
        # 为了防止数据混乱，提前在实例化的时候，将user信息给剔除出去
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ChangePasswordForm,self).__init__(*args,**kwargs)
    # 验证新密码一致性
    def clean(self):
        new_password = self.cleaned_data.get('new_password','')
        new_password_rep = self.cleaned_data.get('new_password_repeatation','')
        if not (new_password != "" and new_password_rep == new_password):
            raise forms.ValidationError("两次密码输入不一致！")
        else:
            return self.cleaned_data
    
    # 验证旧密码是否正确
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password','')
        # 利用自带的check_password()方法对密码进行检查
        if not self.request.user.check_password(old_password):
            raise forms.ValidationError("旧密码不正确，请再次确认后重新输入！")
        return old_password

# 忘记密码
class ForgotPasswordForm(forms.Form):
    bind_email_address_widget = forms.EmailInput(attrs={'class':"form-control",'placeholder':"请输入绑定的邮箱地址"})
    verification_code_widget = forms.TextInput(attrs={'class':"form-control",'placeholder':"请输入邮箱收到的验证码"})
    verification_code_send_btn_widget = forms.TextInput(attrs={'type':'button','class':'btn btn-primary','value':'点击发送验证码'})
    new_password_widget = forms.PasswordInput(attrs={'class':"form-control",'placeholder':"请输入密码"})
    new_password_widget_repeat_widget = forms.PasswordInput(attrs={'class':"form-control",'placeholder':"请重输一遍新的密码"})
    
    bind_email_address = forms.EmailField(label='绑定的邮箱地址',min_length=3,max_length=30,widget=bind_email_address_widget)
    verification_code_for_forget_password = forms.CharField(label='验证码',min_length=3,max_length=8,widget=verification_code_widget)
    verification_code_send_btn_forget_password = forms.CharField(label="",required=False,widget=verification_code_send_btn_widget)
    reset_password = forms.CharField(label='新密码',min_length=6,widget=new_password_widget)
    reset_password_repeatation = forms.CharField(label='新密码验证',min_length=6,widget=new_password_widget_repeat_widget)
    
    # 初始化类的继承
    def __init__(self,*args, **kwargs):
         # 在这里面是为了防止参数混淆，因为user我们可以直接通过request.user去获取，
        # 为了防止数据混乱，提前在实例化的时候，将user信息给剔除出去
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ForgotPasswordForm,self).__init__(*args,**kwargs)

    # 对输入的邮箱地址的有效性验证
    def clean_bind_email_address(self):
        bind_email_address = self.cleaned_data.get('bind_email_address','').strip()
        session_saved_email = self.request.session.get('target_email','')
        if bind_email_address == '':
            raise forms.ValidationError('输入的邮箱地址不能为空！')
        if not User.objects.filter(email = bind_email_address).exists():
            raise forms.ValidationError("邮箱不存在,请输入正确的邮箱地址！")
        # 注意为了安全性，最好将缓存的邮件地址与提交的瞬间的邮件地址做一次比较，不然会产生新的Bug
        if not(session_saved_email !="" and session_saved_email == bind_email_address):
            raise forms.ValidationError("邮件地址和接收验证码邮件地址不一致！")
        return bind_email_address

    # 对输入的验证码做一些验证
    def clean_verification_code_for_forget_password(self):
        verification_code_for_forget_password = self.cleaned_data.get('verification_code_for_forget_password','').strip()
        gen_verification_code = self.request.session.get('forgot_password','')
        # print(verification_code_for_forget_password)
        # print(gen_verification_code)
        if verification_code_for_forget_password == "":
            raise forms.ValidationError("验证码不能为空！")
        if not (gen_verification_code !="" and gen_verification_code == verification_code_for_forget_password):
            raise forms.ValidationError('验证码不正确！')
        return verification_code_for_forget_password

    # 密码验证
    def clean_reset_password_repeatation(self):
        reset_password=self.cleaned_data.get('reset_password','').strip()
        reset_password_repeatation=self.cleaned_data.get('reset_password_repeatation','').strip()
        # print(f'new_password:{reset_password}')
        # print(f'new_password_repeatation:{reset_password_repeatation}')
        if not (reset_password_repeatation != "" and reset_password == reset_password_repeatation):
            raise forms.ValidationError("两次输入的密码不一致，请重新输入！")
        return reset_password_repeatation


# 绑定QQ
class BindQQForm(UserLoginForm):
    username_widget = forms.TextInput(
        attrs={'class': "form-control", 'placeholder': "请输入用户名或邮箱"})
    password_widget = forms.PasswordInput(
        attrs={'class': "form-control", 'placeholder': "请输入密码"})

    username_or_email = forms.CharField(label='用户名|邮箱', widget=username_widget)
    password = forms.CharField(label='密码', widget=password_widget)
    def clean(self):
        submitted_username_or_email = self.cleaned_data.get('username_or_email','').strip()
        submitted_password = self.cleaned_data.get('password','').strip()
        if submitted_username_or_email == '':
            raise forms.ValidationError('用户名不能为空！')
        if submitted_password == '':
            raise forms.ValidationError('输入的密码不能为空！')
        user = authenticate(username=submitted_username_or_email,password=submitted_password)
        # 对验证结果做进一步判断，
        if user is None:
            # 如果用户名验证不通过，就用邮件尝试登录
            if User.objects.filter(email=submitted_username_or_email).exists():
                user_name = User.objects.get(email = submitted_username_or_email ).username
                user = authenticate(username=user_name,password=submitted_password)
                if user:
                    # 如果验证用户存在，那就需要进一步验证QQ是否被重复绑定
                    oauth_relationship = OAuthRelationship.objects.filter(user = user,open_id_type_index = 1)
                    if oauth_relationship.exists():
                        raise ValidationError('该用户已经绑定其他QQ号，不允许重复绑定！')
                    else:
                        # 如果验证该用户没有绑定QQ那就继续进行将QQ绑定用户的逻辑
                        self.cleaned_data['user'] = user
                        return self.cleaned_data
            else:
                raise forms.ValidationError("用户名或密码错误！")
        else:
            # 验证通过，那么返回的user不为空，则将结果存储到cleaned_data这个字典里面，方便我们获取，和减少新字典的申明，可以极大节省内存
            self.cleaned_data['user'] = user
        return self.cleaned_data




    # def clean_username_or_email(self):
    #     user = self.cleaned_data.get('user','').strip()
    #     print(f'user: {user}')
    #     oauth_relationship = OAuthRelationship.objects.filter(user = user,open_id_type_index = 1)
    #     if oauth_relationship.exists():
    #         raise ValidationError('当前用户已经绑定过QQ，不允许重复绑定!')
    #     else:
    #         self.cleaned_data['user'] = user
    #         return self.cleaned_data 



 















