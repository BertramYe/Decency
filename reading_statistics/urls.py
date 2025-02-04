from django.urls import path

from . import views


# app_name = 'articles'


urlpatterns = [
   path('',views.reading_statistics,name='reading_statistics'), # 用户阅读统计
    
]