from . import views
from django.urls import path

urlpatterns = [
    path('schema', views.schema, name='schema'),
]
