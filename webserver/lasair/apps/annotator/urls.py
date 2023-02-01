from . import views
from django.urls import path

urlpatterns = [
    path('annotator/', views.annotators, name='annotators'),
]
