from django.urls import path

from . import views


# app_name = 'articles'


urlpatterns = [
    path('', views.article_list, name="articles_list"),
    path('<int:article_id>',views.article_details, name='article_details'),
    path('<str:articles_type>',views.articles_with_type, name='article_type_name'),
    path('date/<int:year>/<int:month>',views.article_with_date,name='article_with_date'),
]
