from . import views
from django.urls import path

urlpatterns = [
    path('annotator/', views.annotator_index, name='annotator_index'),
    path('annotator/<slug:topic>/', views.annotator_detail, name='annotator_detail'),
]
