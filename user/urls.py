from django.urls import path
from user import views

urlpatterns = [
    path('', views.user, name='user'),
    path('<int:id>/', views.user_arg, name='user_arg'),
    path('<int:id>/delete/', views.user_delete, name='user_delete'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
]
