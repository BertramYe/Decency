"""decency URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('admin/', admin.site.urls),
    path('ckeditor/',include('ckeditor_uploader.urls')),  # 配置ckeditor的路由信息（固定，不可更改）
    path('users_managements/',include('users_managements.urls')),     # 用户操作的路由
    path('articles/', include('articles.urls')),
    path('comment/',include('comments.urls')),
    path('likes/',include('likes.urls')), # 用户点赞
    path('reading_statistics/',include('reading_statistics.urls')), # 用户的文章阅读访问的统计
    path('search',views.page_search,name='page_search'), # 用户搜索
    path('web3D',views.web_3D,name='WEB3D'), # 用户搜索
]

# 添加 MEDIA 映射的路由信息
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)