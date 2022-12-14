from . import views
from django.urls import path

urlpatterns = [
    path('filters/', views.filter_query_index, name='filter_query_index'),
    path('filters/create/', views.filter_query_create, name='filter_create'),
    path('filters/<int:mq_id>/', views.filter_query_detail, name='filter_query_detail'),
    path('filters/log/<slug:topic>/', views.filter_log, name='filter_log')
]
