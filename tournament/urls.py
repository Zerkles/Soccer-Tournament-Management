from django.urls import path
from tournament import views

urlpatterns = [
    path('', views.tournament, name='tournament'),
    path('<int:id>/', views.tournament_arg, name='tournament_arg'),
    path('create/', views.create, name='create'),
    path('<int:id>/delete/', views.tournament_delete, name='tournament_delete'),

    path('<int:tournament_id>/player/', views.player, name='player'),
    path('<int:tournament_id>/player/<int:playerID>/', views.player_arg, name='player_arg'),
    path('<int:tournament_id>/player/<int:playerID>/delete/', views.player_delete, name='player_delete'),

    path('<int:tournament_id>/score/<int:scoreID>/', views.score_arg, name='score_arg'),
]
