"""lasair URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as authviews
from django.urls import include, path
from django.views.generic import TemplateView

from lasair import views, services, objects, areas, watchlists, queries, skymap

from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # REMOVE LATER?
    path('index2/', views.index2, name='index2'),
    path('contact', TemplateView.as_view(template_name='contact.html')),
    path('simple_search', TemplateView.as_view(template_name='simple_search.html')),
    path('annotators/', views.annotators, name='annotators'),



    path('', views.index, name='index'),

    path('conesearch/', views.conesearch, name='conesearch'),
    path('schema', views.schema, name='schema'),
    path('status/', views.status_today, name='status_today'),
    path('status/<int:nid>/', views.status, name='status'),
    path('streams/<slug:topic>/', views.streams, name='streams'),
    path('fitsview/<slug:filename>/', views.fitsview, name='fitsview'),
    path('object/<slug:objectId>/old/', objects.objhtml, name='objhtml'),
    path('object/<slug:objectId>/', objects.object_detail, name='object_detail'),

    path('watchlist-regions/', areas.areas_home, name='watchlist_regions'),
    path('watchlist-regions/create/', areas.area_new, name='watchlist_regions_create'),
    path('watchlist-regions/<int:ar_id>/', areas.show_area, name='watchlist_regions_detail'),
    path('watchlist-regions/<int:ar_id>/file/', areas.show_area_file, name='watchlist_regions_file'),

    path('watchlist-catalogues/', watchlists.watchlists_home, name='watchlist_catalogues'),
    path('watchlist-catalogues/create/', watchlists.watchlist_new, name='watchlist_catalogues_create'),
    path('watchlist-catalogues/<int:wl_id>/', watchlists.show_watchlist, name='watchlist_catalogues_detail'),
    path('watchlist-catalogues/<int:wl_id>/txt/', watchlists.show_watchlist_txt, name='show_watchlist_txt'),

    path('watchlist-smart/<slug:which>/', queries.querylist, name='watchlist_smart'),


    path('querylist/<slug:which>/', queries.querylist, name='querylist'),
    path('query/', queries.new_myquery, name='new_myquery'),
    path('query/<int:mq_id>/', queries.show_myquery, name='show_myquery'),


    path('runquery/', queries.runquery_post, name='runquery_post'),
    path('runquery/<int:mq_id>/', queries.runquery_db, name='runquery_db'),

    path('skymap/', skymap.skymap, name='skymap'),
    path('skymap/<skymap_id_version>/', skymap.show_skymap, name='show_skymap'),

    path('fits/<slug:candid_cutoutType>/', services.fits, name='fits'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('admin/', admin.site.urls),
    path('', include('lasairapi.urls')),
    path('', include('users.urls')),

    path("__reload__/", include("django_browser_reload.urls")),
]


# ADD DJANGO DEBUG TOOLBAR
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
