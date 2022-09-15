from . import views
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('simple_search', TemplateView.as_view(template_name='simple_search.html')),
    path('conesearch/', views.conesearch, name='conesearch'),
]
