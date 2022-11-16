from django.urls import path
from . import views_tmdb

urlpatterns = [
    path('tmdb/', views_tmdb.tmdb_data),
    path('movies/', views_tmdb.movie_list),
    path('overview/', views_tmdb.overview_sim),
    path('title/', views_tmdb.title_sim),
    path('genre/', views_tmdb.genre_sim),
]