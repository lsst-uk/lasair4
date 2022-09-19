from . import views
from django.urls import path

urlpatterns = [
    path('watchlist-regions/', views.watchlist_region_index, name='watchlist_region_index'),
    path('watchlist-regions/create/', views.watchlist_region_create, name='watchlist_region_create'),
    path('watchlist-regions/<int:ar_id>/', views.watchlist_region_detail, name='watchlist_region_detail'),
    path('watchlist-regions/<int:ar_id>/file/', views.watchlist_region_download, name='watchlist_region_download'),
]
