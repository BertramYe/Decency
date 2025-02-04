from .forms import UserLoginForm


# 将指定的登录forms页面做成公共的模板
def login_form_model(request):
    return {'login_form_model':UserLoginForm()}