# 导入string和random以及time库做时间戳，为生成随机验证码做准备
import string,random
# 导入重定向模块
from django.shortcuts import render,redirect
# 导入用户验证模块用来做用户登录验证
from django.contrib.auth import authenticate,login,logout
# 导入用户模型
from django.contrib.auth.models import User
# 导入reverse，可以反向解析路由信息
from django.urls import reverse
# 导入json转化模块，为我们前端的Json文件做准备
from django.http import JsonResponse
# 导入我们利用django自带的form表单定义的用户登录和注册表单类,以及用户信息修改
from .forms import UserLoginForm,UserRegisterForm,ChangeNickNameForm,BindEmailForm,ChangePasswordForm,ForgotPasswordForm,BindQQForm
# 导入自定义的邮件发送模块
from decency.utils import SendEmail
# 导入获取QQ信息模块
from .utils import get_qq_access_token, get_qq_openid,get_qq_user_infor
# 导入配置文件信息
from decency import settings
# 导入我们自定义的模型
from .models import UserProfile,OAuthRelationship,OpenIDType


# 用户登录界面
def userlogin(request):
    '''
    #利用request请求，里面的POST方法，它内部携带的信息，我们通过get获取用户登录时form表单输入的用户名信息，
    # 如果用户名为none，那么我们就令其值为默认为空
    login_username = request.POST.get('username','')
    login_password = request.POST.get('password','')
    # 利用  authenticate（）方法对用户登录的信息进行验证,如果验证通过，就会输出（user）用户名信息
    user = authenticate(request,username =login_username,password=login_password)
    # 利用request头部携带的路径跳转信息，我们用于做登录的路径跳转
    # 登陆成功跳转到当前页面，如果当前页面获取不到，就跳转到首页
    # reverse()反向解析homepage这个路由url的信息
    redirections_path = request.META.get('HTTP_REFERER',reverse('homepage'))
    if user is not None:
        # user 信息不为空，也就是验证通过，登录成功
        login(request,user)
        # 重定向跳转到首页
        return redirect(redirections_path)  
    else:
        # 验证不通过，重定向跳转到我们指定页面进行重新登录
        return render(request,'error.html',{'error_message':'用户名或密码不正确！','redirections_path':redirections_path}) 
    '''
    if request.method=="POST":
        # 将前端登陆页面利用POST传过来的登录信息，进行实例化
        userlogin_submit_forms = UserLoginForm(request.POST)
        if userlogin_submit_forms.is_valid():
            # 表单验证通过会返回一个cleaned_data的字典存储表单信息，
            # 利用cleaned_data获取表单里面干净的数据信息,进行用户名和密码信息验证
            # verify_result= userlogin_submit_forms.verify_user_login()
            # verify_user_login验证完会返回一个verify_result新的cleaned_data对象，
            # 我们重新获取里面的user信息（验证的结果），进行登录操作
            # if verify_result['error_message'] is None:
            #     login(request,verify_result['user'])
            #     # 利用get请求里面的前端传进来的键值对信息，也就是？后面携带的路径信息，重定向跳转回去
            #     redirections_path = request.GET.get('login_from',reverse('homepage'))
            #     return redirect(redirections_path)
            # else:
            #     # userlogin_submit_forms.add_error(None,"用户名或密码错误！！！")
            #     userlogin_submit_forms.add_error(None,verify_result['error_message'])
            
            # 除了以上方式，还可以直接用下面方式登录，减少了对验证结果的判断，
            # 这是因为借住了forms类里面内置的clean（）方法，无需调用，可以直接调用结果,因为当他被实例化时，clean方法就被执行了
            # 也只有执行了is_valid()，才会生成一个cleaned_data的字典对象，这个字典里面存储了验证的结果的表单信息
            user= userlogin_submit_forms.cleaned_data["user"]
            login(request,user)
            redirections_path = request.GET.get('login_from',reverse('homepage'))
            return redirect(redirections_path)
    else:
        # 否则就是GET请求
        # 直接实例化我们定义的表单类，并将表单信息传给前端
        userlogin_submit_forms = UserLoginForm()
    contenttext ={}
    contenttext['userlogin_forms']=userlogin_submit_forms
    contenttext['page_name']='用户登录'
    contenttext['form_name']='用户登录'
    return render(request,'users_managements/userlogin.html',contenttext)

# 重新做一个view方法，进行登录弹窗的验证
def user_login_model(request):
    data = {}
    if request.method=="POST":
        userlogin_submit_forms = UserLoginForm(request.POST)
        if userlogin_submit_forms.is_valid():
            user= userlogin_submit_forms.cleaned_data["user"]
            login(request,user)
            data['login_status'] = 'SUCCESS'
        else:
            data['login_status'] = 'ERROR'
    
    return JsonResponse(data)

# 用户用QQ登录
def login_with_qq(request):
    authorization_code = request.GET.get('code','')
    state = request.GET.get('state','')
    if state != settings.QQ_STATE:
        raise Exception('state 状态不对!')
    else:
        qq_access_token= get_qq_access_token(authorization_code)
        # 如果qq_access_token是False表示登陆过期,否则正确返回
        if qq_access_token == False:
            # 获取openid的
            raise Exception('access_token have expired! please have a retry!')
        else:
            qq_open_id = get_qq_openid(qq_access_token)
            # 将open_id和qq_access_token存储到session里面,为QQ绑定做准备
            request.session['qq_open_id'] = qq_open_id
            request.session['qq_access_token'] = qq_access_token
            # open_id_type_index = 1 表示QQ登录
            oauth_relationship = OAuthRelationship.objects.filter(open_id = qq_open_id, open_id_type_index = 1)
            if oauth_relationship.exists():
                # 如果可以查到用户已经绑定QQ登陆的信息，那就让用户正常登录，并返回首页
                user = OAuthRelationship.objects.get(open_id = qq_open_id, open_id_type_index = 1).user
                login(request,user)
                return redirect(reverse('homepage'))
            else:
                # 如果查不到，那就要让用户绑定QQ
                # 1. 用户在本网站有用户名和密码
                # 2. 用户在本网站没有用户名和密码 --- 虽然有人会让用户直接一键创建用户，但是在这里我还是会要求用户进行用户的注册
                # 3. 用户在本站有用户名和密码，但是绑定的是其他QQ用户信息
                return redirect(reverse('bind_qq'))

# 用户绑定QQ
def bind_qq(request):
    contenttext ={}
    # 在做用户与QQ绑定之前我们也可以将用户的基本信息获取并显示出来
    # 获取QQ用户的头像和用户名信息
    qq_access_token = request.session.get('qq_access_token','')
    qq_open_id = request.session.get('qq_open_id','')
    get_qq_user_infor_reponse = get_qq_user_infor(qq_access_token,qq_open_id)
    qq_ret_code = get_qq_user_infor_reponse['ret'] 
    if qq_ret_code != 0:
        # ret为0表示成功获取到用户信息
        error_msg = get_qq_user_infor_reponse['msg']
        raise Exception(f'请求用户信息失败，请返回登陆页面重新去登录QQ！error：{error_msg}')
    else:
        qq_user_nick_name = get_qq_user_infor_reponse['nickname']
        qq_user_figure = get_qq_user_infor_reponse['figureurl']
        # 将获取到的信息反馈给前端页面
        contenttext['qq_user_nick_name'] = qq_user_nick_name
        contenttext['qq_user_figure'] = qq_user_figure
    # 利用验证用户的用户名和密码的方式来让用户绑定QQ
    if request.method=="POST":
        # 将前端登陆页面利用POST传过来的登录信息，进行实例化
        userlogin_submit_forms = BindQQForm(request.POST)
        if userlogin_submit_forms.is_valid():
            # 如果获取的用户名和密码都正确，获取并清除我们存储的qq_open_id，开始绑定QQ
            qq_open_id = request.session.pop('qq_open_id')
            # 顺带将qq_access_token也给清除了
            qq_access_token = request.session.pop('qq_access_token')
            user= userlogin_submit_forms.cleaned_data["user"]
            # 开始绑定
            # 因为OAuthRelationship被关联到了另一张表OpenIDType故而最好检查一下这张表里面到底有没有对应的关系,
            # 如果没有，就添加以下
            open_id_type,open_id_type_create = OpenIDType.objects.get_or_create(open_id_type_index =1,open_id_type_name = 'QQ')
            # 并将获取open_id_type_index用来绑定
            # 进一步存储我们想要的信息
            oauth_relationship = OAuthRelationship()
            oauth_relationship.user = user
            # open_id_type_index_id是因为在django里面它会在对应的外键后面加上"_id"用来标识
            # 此处虽然我们在model里面定义的是open_id_type_index，但是它在DB里面的生成时会自动在我们定义的外键后面加上id的字样
            oauth_relationship.open_id_type_index_id= open_id_type.open_id_type_index
            oauth_relationship.open_id = qq_open_id
            oauth_relationship.save()
            # 绑定QQ完成并自登录，自动跳转到首页
            login(request,user)
            return redirect(reverse('homepage'))
        # 否则就是GET请求
        # 直接实例化我们定义的表单类，并将表单信息传给前端
    else:
        userlogin_submit_forms = BindQQForm()
    contenttext['userlogin_forms']=userlogin_submit_forms
    contenttext['page_name']='绑定QQ'
    # contenttext['form_name']='QQ绑定:'
    return render(request,'users_managements/bind_qq.html',contenttext)


# 用户登出操作
def userloginout(request):
    # 登出很简单，直接登出就可以了
    logout(request)
    # 同时我们利用登出的时候也直接跳转到当前登出的页面
    redirections_path = request.GET.get('login_from',reverse('homepage'))
    return redirect(redirections_path) 

# 用户注册
def userregister(request):
    if request.method=="POST":
        userregister_submit_forms = UserRegisterForm(request.POST,request=request)
        if userregister_submit_forms.is_valid():
            # 如果验证通过，那么就获取信息，在models里面写入注册信息
            register_username =  userregister_submit_forms.cleaned_data['username']
            register_email =  userregister_submit_forms.cleaned_data['email']
            register_password =  userregister_submit_forms.cleaned_data['password_repeatation_for_register']
            # register_password =  userregister_submit_forms.cleaned_data['password_repeatation']
            # 创建写入注册信息
            register_user =  User.objects.create_user(register_username,register_email,register_password)
            register_user.save()
            # 注意，在这里最好加一个清除session验证码的步骤，这样使得避免重复注册，和安全
            # 清除session里面的注册的邮箱绑定字段
            del request.session['new_user_register']
            
            # 用户验证登录
            user = authenticate(username =register_username,password=register_password)
            login(request,user)
            redirections_path = request.GET.get('login_from',reverse('homepage'))
            return redirect(redirections_path)
    else:
        userregister_submit_forms = UserRegisterForm()
    contenttext ={}
    contenttext['page_title'] = '用户注册'
    contenttext['form_title'] = '用户注册'
    contenttext['userregister_forms']=userregister_submit_forms
    contenttext['submit_text'] = '点击注册'
    return render(request,'users_managements/userregister.html',contenttext)

# 用户信息详情页
def userinformation(request):
    context = {}
    return render(request,'users_managements/user_information.html',context)

# 修改用户信息
# 修改用户昵称
def change_nickname(request):
    redirections_path = request.GET.get('from_page',reverse('homepage'))
    if request.method == 'POST':
        # 如果是POST请求，那就传入对应的form表单里面，并且将当前session的用户信息传入进去用于后台的信息验证
        change_information_form = ChangeNickNameForm(request.POST,user=request.user)
        if change_information_form.is_valid():
        # 如果验证输入的信息通过，那就进行昵称的修改动作
            new_nickname = change_information_form.cleaned_data['new_nickname']
            # 当前用户昵称可能为空，为了防止昵称为空，即当昵称没有时，我们就创建它
            userprofile,created = UserProfile.objects.get_or_create(user = request.user)
            # 修改用户昵称
            userprofile.nickname = new_nickname
            userprofile.save()
            # 保存完成后跳转回个人资料页面
            return redirect(redirections_path)
    else:
        change_information_form = ChangeNickNameForm()
    context = {}
    context['page_title'] = '修改用户昵称'
    context['form_title'] = '修改用户昵称'
    context['change_information_form'] = change_information_form
    context['submit_text'] = '点击修改'
    context['redirections_path'] = redirections_path
    return render(request,"users_managements/change_user_information.html",context)

# 邮箱的绑定操作
def bind_email(request):
    redirections_path = request.GET.get('from_page',reverse('homepage'))
    if request.method == 'POST':
        # 如果是POST请求，那就传入对应的form表单里面，并且将当前session的用户信息传入进去用于后台的信息验证
        change_information_form = BindEmailForm(request.POST,request=request)
        if change_information_form.is_valid():
        # 如果验证输入的信息通过，那就进行邮箱的绑定、修改的动作
            to_bind_email = change_information_form.cleaned_data['new_email_address']
            request.user.email = to_bind_email
            request.user.save()
            # 注意，在这里最好加一个清除session验证码的步骤，这样使得避免重复注册，和安全
            # 清除session里面的修改邮箱的验证码信息字段，防止验证码被滥用
            del request.session['bind_email_address']
            # 保存完成后跳转回个人资料页面
            return redirect(redirections_path)
    else:
        change_information_form = BindEmailForm()
    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '修改邮箱'
    context['change_information_form'] = change_information_form
    context['submit_text'] = '点击修改'
    context['redirections_path'] = redirections_path
    return render(request,"users_managements/change_user_information.html",context)

# 邮箱发送验证码
def send_email_with_verify_code(request):
    target_email = request.GET.get('email','')
    send_email_for = request.GET.get('send_email_for','')
    email_exist_or_not = User.objects.filter(email = target_email).exists()
    data = {}  # 为前端交互做准备
    if target_email != '':
        # 在发送邮件之前，根据不同的情形，选择是否发送邮件，这样可以减少不必要的邮件的发送，减少资源消耗
        if send_email_for == 'bind_email_address' and email_exist_or_not:
            data['status'] = 'ERROR_EMAIL_REPEAT'
        elif send_email_for =='new_user_register' and  email_exist_or_not:
            data['status'] = 'ERROR_EMAIL_REPEAT'
        elif send_email_for =='forgot_password' and email_exist_or_not == False:
            data['status'] = 'ERROR_EMAIL_NOT_EXIST'
        else:
            # 生成验证码(大小写的英文加上数字，拼接起来取其中的任意四个)
            verification_code ="".join(random.sample(string.ascii_letters + string.digits,4))   
            # 同时利用连接的session 存储我们生成的验证码，默认存储的有效期为两星期
            request.session[send_email_for] = verification_code
            # 为了防止在邮件绑定过程中，用户拿到验证码后，突然修改邮箱，最好也一起将用户输入的邮箱地址存储在缓存里面，用以备用比对
            request.session['target_email'] = target_email
            # 设置过期时间，0，代表浏览器关闭，那么session就过期
            request.session.set_expiry(0)
            # 发送验证码
            # 利用自定义的邮件发送模块，进行验证码发送，单独开线程利用异步，专门发邮件，可以减少网页提交负担
            email_sending = SendEmail("Verification_Code",target_email,verification_code)
            email_sending.start()
            # 邮件发送成功给前端反馈一个状态信息
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)
    
# 修改密码
def change_password(request):
    redirections_path = request.GET.get('from_page',reverse('userlogin'))
    context = {}
    context['forgot_password_or_not'] =False
    # 如果用户已登录
    if request.user.is_authenticated:
        # 如果是POST请求，那就传入对应的form表单里面，并且将当前session的用户信息传入进去用于后台的信息验证
        if request.method == 'POST':
            # 如果用户已经登陆，那就直接修改密码
            change_information_form = ChangePasswordForm(request.POST,request=request)
            if change_information_form.is_valid():
            # 如果验证输入的信息通过，那就进行密码修改动作
                user = request.user
                new_password = change_information_form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                # 密码修改完成后，删除session里面的验证码信息
                del request.session['forgot_password']
                # 退出用户登录
                logout(request)
                # 退出后跳转回用户登录页面，并且需要用户重新登录
                return redirect(redirections_path)
        else:
            change_information_form = ChangePasswordForm()
        context['page_title'] = '修改密码'
        context['form_title'] = '重置密码'
    else:
        # 如果未登录，则就是需要邮箱验证后，重置密码（忘记密码的逻辑）
        context['forgot_password_or_not'] = True
        if request.method == 'POST':
            # 点击忘记密码，并且发了POST请求，那就需要邮箱验证
            change_information_form = ForgotPasswordForm(request.POST,request=request)
            if change_information_form.is_valid():
                user_email = change_information_form.cleaned_data['bind_email_address']
                user = User.objects.get(email=user_email)
                new_password = change_information_form.cleaned_data['reset_password_repeatation']
                user.set_password(new_password)
                user.save()
                # 密码修改完成后，保存并退出用户登录
                # 同时删除session里面的验证码信息
                del request.session['forgot_password']
                return redirect(redirections_path)
        else:
            change_information_form = ForgotPasswordForm()
        context['page_title'] = '忘记密码'
        context['form_title'] = '重置密码'
    context['change_information_form'] = change_information_form
    context['submit_text'] = '点击修改'
    context['redirections_path'] = redirections_path
    return render(request,"users_managements/change_user_information.html",context)