from . import views
from django.urls import path

urlpatterns = [
    path('skymap/', views.skymap, name='skymap'),
    path('skymap/<skymap_id_version>/', views.show_skymap, name='show_skymap'),
]
