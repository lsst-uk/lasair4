from . import views
from django.urls import path

urlpatterns = [
    path('annotator/', views.annotator_index, name='annotator_index'),
]
