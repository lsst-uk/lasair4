from . import views
from django.urls import path

urlpatterns = [
    path('filters/', views.filter_query_index, name='filter_query_index'),
    path('filters/new/', views.handle_myquery, name='filter_create'),
    path('filters/<int:mq_id>/', views.filter_query_detail, name='filter_query_detail'),
    path('filters/log/<slug:topic>/', views.filter_log, name='filter_log'),

    # NEED UPDATED
    path('filters/<slug:which>/', views.querylist, name='filters'),
    path('querylist/<slug:which>/', views.querylist, name='querylist'),
    path('runquery/', views.runquery_post, name='runquery_post'),
]
