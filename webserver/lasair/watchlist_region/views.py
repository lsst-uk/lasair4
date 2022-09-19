from .models import Areas
import tempfile
import io
import base64
import time
import json
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.coordinates import Angle, SkyCoord
from mocpy import MOC, World2ScreenMPL
from subprocess import Popen, PIPE
from random import randrange
from lasair import settings
from django.utils.text import slugify
from django.http import HttpResponse, FileResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from django.shortcuts import render, get_object_or_404
from src import db_connect
import sys
from . import bytes2string, string2bytes, make_image_of_MOC
sys.path.append('../common')


def watchlist_region_download(request, ar_id):
    """*download the original region file used to create the watchlist region*

    **Key Arguments:**

    - `request` -- the original request
    - `ar_id` -- UUID of the watchlist region

    **Usage:**

    ```python
    urlpatterns = [
        ...
         path('watchlist-regions/<int:ar_id>/file/', views.watchlist_region_download, name='watchlist_region_download'),
        ...
    ]
    ```           
    """
    message = ''
    area = get_object_or_404(Areas, ar_id=ar_id)

    is_owner = (request.user.is_authenticated) and (request.user == area.user)
    is_public = (area.public == 1)
    is_visible = is_owner or is_public
    if not is_visible:
        return render(request, 'error.html', {
            'message': "This area is private and not visible to you"})

    moc = string2bytes(area.moc)

    filename = slugify(area.name) + '.fits'
    tmpfilename = tempfile.NamedTemporaryFile().name + '.fits'
    f = open(tmpfilename, 'wb')
    f.write(moc)
    f.close()

    r = HttpResponse(moc)
    r['Content-Type'] = "application/fits"
    r['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return r


def watchlist_region_detail(request, ar_id):
    """*summary of function*

    **Key Arguments:**

    - `request` -- the original request
    - `ar_id` -- UUID of the watchlist region

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchlist-regions/<int:ar_id>/', views.watchlist_region_detail, name='watchlist_region_detail'),
        ...
    ]
    ```           
    """
    message = ''
    area = get_object_or_404(Areas, ar_id=ar_id)

    is_owner = (request.user.is_authenticated) and (request.user == area.user)
    is_public = (area.public == 1)
    is_visible = is_owner or is_public
    if not is_visible:
        return render(request, 'error.html', {
            'message': "This area is private and not visible to you"})

    if request.method == 'POST' and is_owner:
        if 'name' in request.POST:
            area.name = request.POST.get('name')
            area.description = request.POST.get('description')

            if request.POST.get('active'):
                area.active = 1
            else:
                area.active = 0

            if request.POST.get('public'):
                area.public = 1
            else:
                area.public = 0

            area.save()
            message += 'area updated'

    msl = db_connect.readonly()
    cursor = msl.cursor()
    cursor.execute('SELECT count(*) AS count FROM area_hits WHERE ar_id=%d' % ar_id)
    for row in cursor:
        count = row[0]

    cursor.execute('SELECT objectId FROM area_hits WHERE ar_id=%d LIMIT 1000' % ar_id)
    objIds = []
    for row in cursor:
        objIds.append(row[0])

    return render(request, 'watchlist_region/watchlist_region_detail.html', {
        'area': area,
        'objIds': objIds,
        'mocimage': area.mocimage,
        'count': count,
        'is_owner': is_owner,
        'message': message})


@csrf_exempt
def watchlist_region_index(request):
    """*return a list of public and user owned watchlist regions*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchlist-regions/', views.watchlist_region_index, name='watchlist_region_index'),
        ...
    ]
    ```           
    """
    message = ''
    if request.method == 'POST' and request.user.is_authenticated:
        delete = request.POST.get('delete')

        if delete == None:   # create new area

            t = time.time()
            name = request.POST.get('name')
            description = request.POST.get('description')

            if 'area_file' in request.FILES:
                fits_bytes = (request.FILES['area_file']).read()
                fits_string = bytes2string(fits_bytes)
                png_bytes = make_image_of_MOC(fits_bytes)
                png_string = bytes2string(png_bytes)

                area = Areas(user=request.user, name=name, description=description,
                             moc=fits_string, mocimage=png_string, active=0)
                area.save()
                message += '\nArea created successfully in %.1f sec' % (time.time() - t)
            else:
                message = '\nNo file in upload'
        else:
            ar_id = int(delete)
            area = get_object_or_404(Areas, ar_id=ar_id)
            if request.user == area.user:
                area.delete()
                message = 'Area %s deleted successfully' % area.name

    other_areas = Areas.objects.filter(public=1)
    if request.user.is_authenticated:
        my_areas = Areas.objects.filter(user=request.user)
    else:
        my_areas = []

    return render(request, 'watchlist_region/watchlist_region_index.html',
                  {'my_areas': my_areas,
                   'random': '%d' % randrange(1000),
                   'other_areas': other_areas,
                   'authenticated': request.user.is_authenticated,
                   'message': message})


def watchlist_region_create(request):
    """*create a new watchlist region*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchlist-regions/create/', views.watchlist_region_create, name='watchlist_region_create'),
        ...
    ]
    ```           
    """
    return render(request, 'watchlist_region/watchlist_region_create.html',
                  {'random': '%d' % randrange(1000),
                   'authenticated': request.user.is_authenticated
                   })
