from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 主页
    path('about/', views.about, name='about'),  # 关于页面
    path('contact/', views.contact, name='contact'),  # 联系页面
]