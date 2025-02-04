import json
from urllib import parse
# 导入链接打开模块
from urllib.request import urlopen
from urllib.parse import parse_qs
# 导入配置文件
from decency import settings

# 获取QQ用户登陆的ACCESS_TOKEN
def get_qq_access_token(authorization_code):
    params = {
        'grant_type':settings.QQ_GRANT_TYPE,
        'client_id' : settings.QQ_APPID,
        'client_secret'	:settings.QQ_APP_KEY,
        'code':	authorization_code,
        'redirect_uri':settings.QQ_REDIRECT_URL,
    }
    callback_url = settings.QQ_GET_ACCESS_TOKEN_URL +'?' + parse.urlencode(params)
    access_token_url_response = urlopen(callback_url)
    access_token_url_result= access_token_url_response.read().decode('utf-8')
    access_token_url_data = parse_qs(access_token_url_result)
    # 如果返回的结果不为空，就返回有效的qq_access_token，否则就表示登陆时间太长，登陆过期直接返回False
    if bool(access_token_url_data) != False:
        qq_access_token = access_token_url_data['access_token'][0]
        return qq_access_token
    else:
        return False

# 将返回的url链接解析成我们想要的字典的格式

# 获取QQ用户的OPENID完成QQ用户的网站登录操作
def get_qq_openid(access_token):
    params = {
        'access_token':access_token
    }
    callback_url = settings.QQ_GET_OPENID_URL + '?'+ parse.urlencode(params)
    # 获取openid的链接
    qq_openid_url_response = urlopen(callback_url)
    qq_openid_url_result =qq_openid_url_response.read().decode('utf-8')
    qq_openid_url_data = qq_openid_url_result[10:-4].strip()
    # 将字符串的字典格式转化成字典
    qq_openid_url_dict = eval(qq_openid_url_data)
    # 获取openid
    openid = qq_openid_url_dict['openid']
    return openid

# 获取QQ用户的信息
def get_qq_user_infor(access_token,open_id):
    params = {
        "access_token": access_token,
        "oauth_consumer_key":settings.QQ_APPID,
        "openid":open_id,
    }
    callback_url = settings.QQ_GET_USER_INFOR_URL +'?'+parse.urlencode(params)
    qq_get_user_infor_response = urlopen(callback_url)
    user_infor_list = qq_get_user_infor_response.read().decode('utf-8')
    data = json.loads(user_infor_list)
    return data