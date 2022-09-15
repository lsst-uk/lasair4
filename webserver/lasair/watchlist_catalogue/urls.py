from . import views
from django.urls import path

urlpatterns = [
    path('watchlist-catalogues/', views.watchlists_home, name='watchlist_catalogues'),
    path('watchlist-catalogues/create/', views.watchlist_new, name='watchlist_catalogues_create'),
    path('watchlist-catalogues/<int:wl_id>/', views.show_watchlist, name='watchlist_catalogues_detail'),
    path('watchlist-catalogues/<int:wl_id>/txt/', views.show_watchlist_txt, name='show_watchlist_txt'),

]
