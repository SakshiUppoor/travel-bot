from django.urls import path
from . import views

app_name = 'conversation'


urlpatterns = [
    path('', views.chat, name="chat"),
    path('register/', views.register, name="register"),
    path('login/', views.user_login, name="user_login"),
    path('logout/', views.user_logout, name="user_logout"),
]
