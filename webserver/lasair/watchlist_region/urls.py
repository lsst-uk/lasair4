from . import views
from django.urls import path

urlpatterns = [
    path('watchlist-regions/', views.areas_home, name='watchlist_regions'),
    path('watchlist-regions/create/', views.area_new, name='watchlist_regions_create'),
    path('watchlist-regions/<int:ar_id>/', views.show_area, name='watchlist_regions_detail'),
    path('watchlist-regions/<int:ar_id>/file/', views.show_area_file, name='watchlist_regions_file'),
]
