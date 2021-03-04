"""Projeto1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from django.contrib.auth import views as auth_views
from NutriFit import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.base),
    path('home/', views.homepage, name='homepage'),
    path('calculate/', views.calculate, name='calculate'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='/home'), name='logout'),
    path('signIn/', views.signIn, name='signin'),
    path('profile/<str:tab>', views.profile, name='profile'),
    path('daily/', views.daily, name='daily'),
    path('daily/<str:data>/', views.daily, name='daily'),
    path('meal/<int:id>/', views.meal, name='meal'),
    path('validateFood/<int:id_meal>/<int:id_food>/', views.validateFood, name='validateFood'),
    path('removeComposta/<int:food_id>/<int:meal_id>/<str:data>/', views.removeComposta, name='removeComposta'),
    path('food/<int:food_id>/', views.food, name='food'),
    path('food/', views.food, name='food'),
    path('removeFood/<int:food_id>/', views.removeFood, name='removeFood'),
    path('user_management/', views.user_management, name='user management'),
    path('promote_user/<int:id>/', views.promoteUser, name='promote user'),
    path('demote_user/<int:id>/', views.demoteUser, name='demote user'),
    #Adicionar
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]
