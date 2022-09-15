from . import views
from django.urls import path


urlpatterns = [
    path('object/<slug:objectId>/old/', views.objhtml, name='objhtml'),
    path('object/<slug:objectId>/', views.object_detail, name='object_detail'),
]
