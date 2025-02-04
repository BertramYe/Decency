# 记住而在调用时先需要{% load %} 操作
from django import template
from urllib import parse
from decency import settings
# 注册我们自定义的函数
register = template.Library()

@register.simple_tag
def get_qq_login_url():
    params = {
        "response_type" : settings.QQ_RESPONSE_TYPE,
        "client_id" : settings.QQ_APPID,
        "redirect_uri" : settings.QQ_REDIRECT_URL,
        "state" :settings.QQ_STATE,	
    }

    callback_url = settings.QQ_LOGIN_AUTH_PAGE_URL + "?"+ parse.urlencode(params)
    return callback_url