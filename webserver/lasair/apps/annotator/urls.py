from . import views
from django.urls import path

urlpatterns = [
    path('annotators/', views.annotators, name='annotators'),
]
