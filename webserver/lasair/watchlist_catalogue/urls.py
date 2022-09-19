from . import views
from django.urls import path

urlpatterns = [
    path('watchlist-catalogues/', views.watchlist_catalogue_index, name='watchlist_catalogue_index'),
    path('watchlist-catalogues/create/', views.watchlist_catalogue_create, name='watchlist_catalogue_create'),
    path('watchlist-catalogues/<int:wl_id>/', views.watchlist_catalogue_detail, name='watchlist_catalogue_detail'),
    path('watchlist-catalogues/<int:wl_id>/cat/', views.watchlist_catalogue_download, name='watchlist_catalogue_download'),
]
