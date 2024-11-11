from django.urls import path

from . import views

urlpatterns = [
    path('ide/', views.homepage, name=""),

    path('register', views.register, name="register"),

    path('my-login', views.my_login, name="my-login"),

    path('', views.home,name="home"),

    path('user-logout', views.user_logout, name="user-logout"),


    path('run/',views.runcode),
]