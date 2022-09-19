from . import views
from django.urls import path


urlpatterns = [
    path('objects/<slug:objectId>/', views.object_detail, name='object_detail'),
]
