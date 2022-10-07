from .models import Watchmap
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
from . import bytes2string, string2bytes, make_image_of_MOC, add_watchmap_metadata
sys.path.append('../common')


def watchmap_download(request, ar_id):
    """*download the original watchmap file used to create the Watchmap*

    **Key Arguments:**

    - `request` -- the original request
    - `ar_id` -- UUID of the Watchmap

    **Usage:**

    ```python
    urlpatterns = [
        ...
         path('watchmaps/<int:ar_id>/file/', views.watchmap_download, name='watchmap_download'),
        ...
    ]
    ```           
    """
    message = ''
    watchmap = get_object_or_404(Watchmap, ar_id=ar_id)

    is_owner = (request.user.is_authenticated) and (request.user == Watchmap.user)
    is_public = (Watchmap.public == 1)
    is_visible = is_owner or is_public
    if not is_visible:
        return render(request, 'error.html', {
            'message': "This watchmap is private and not visible to you"})

    moc = string2bytes(Watchmap.moc)

    filename = slugify(Watchmap.name) + '.fits'
    tmpfilename = tempfile.NamedTemporaryFile().name + '.fits'
    f = open(tmpfilename, 'wb')
    f.write(moc)
    f.close()

    r = HttpResponse(moc)
    r['Content-Type'] = "application/fits"
    r['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return r


def watchmap_detail(request, ar_id):
    """*summary of function*

    **Key Arguments:**

    - `request` -- the original request
    - `ar_id` -- UUID of the Watchmap

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchmaps/<int:ar_id>/', views.watchmap_detail, name='watchmap_detail'),
        ...
    ]
    ```           
    """
    message = ''
    watchmap = get_object_or_404(Watchmap, ar_id=ar_id)

    is_owner = (request.user.is_authenticated) and (request.user == Watchmap.user)
    is_public = (Watchmap.public == 1)
    is_visible = is_owner or is_public
    if not is_visible:
        return render(request, 'error.html', {
            'message': "This watchmap is private and not visible to you"})

    if request.method == 'POST' and is_owner:
        if 'name' in request.POST:
            Watchmap.name = request.POST.get('name')
            Watchmap.description = request.POST.get('description')

            if request.POST.get('active'):
                Watchmap.active = 1
            else:
                Watchmap.active = 0

            if request.POST.get('public'):
                Watchmap.public = 1
            else:
                Watchmap.public = 0

            Watchmap.save()
            message += 'watchmap updated'

    msl = db_connect.readonly()
    cursor = msl.cursor()
    cursor.execute('SELECT count(*) AS count FROM area_hits WHERE ar_id=%d' % ar_id)
    for row in cursor:
        count = row[0]

    cursor.execute('SELECT objectId FROM area_hits WHERE ar_id=%d LIMIT 1000' % ar_id)
    objIds = []
    for row in cursor:
        objIds.append(row[0])

    return render(request, 'watchmap/watchmap_detail.html', {
        'watchmap': watchmap,
        'objIds': objIds,
        'mocimage': Watchmap.mocimage,
        'count': count,
        'is_owner': is_owner,
        'message': message})


@csrf_exempt
def watchmap_index(request):
    """*return a list of public and user owned watchmaps*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchmaps/', views.watchmap_index, name='watchmap_index'),
        ...
    ]
    ```           
    """
    message = ''
    if request.method == 'POST' and request.user.is_authenticated:
        delete = request.POST.get('delete')

        if delete == None:   # create new watchmap

            t = time.time()
            name = request.POST.get('name')
            description = request.POST.get('description')

            if 'watchmap_file' in request.FILES:
                fits_bytes = (request.FILES['watchmap_file']).read()
                fits_string = bytes2string(fits_bytes)
                png_bytes = make_image_of_MOC(fits_bytes)
                png_string = bytes2string(png_bytes)

                watchmap = Watchmap(user=request.user, name=name, description=description,
                                    moc=fits_string, mocimage=png_string, active=0)
                Watchmap.save()
                message += '\nWatchmap created successfully in %.1f sec' % (time.time() - t)
            else:
                message = '\nNo file in upload'
        else:
            ar_id = int(delete)
            watchmap = get_object_or_404(Watchmap, ar_id=ar_id)
            if request.user == Watchmap.user:
                Watchmap.delete()
                message = 'Watchmap %s deleted successfully' % Watchmap.name

    other_watchmaps = Watchmap.objects.filter(public__gte=1)
    other_watchmaps = add_watchmap_metadata(other_watchmaps, remove_duplicates=True)
    if request.user.is_authenticated:
        my_watchmaps = Watchmap.objects.filter(user=request.user)
        my_watchmaps = add_watchmap_metadata(my_watchmaps)
    else:
        my_watchmaps = []

    return render(request, 'watchmap/watchmap_index.html',
                  {'my_watchmaps': my_watchmaps,
                   'random': '%d' % randrange(1000),
                   'other_watchmaps': other_watchmaps,
                   'authenticated': request.user.is_authenticated,
                   'message': message})


def watchmap_create(request):
    """*create a new Watchmap*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchmaps/create/', views.watchmap_create, name='watchmap_create'),
        ...
    ]
    ```           
    """
    return render(request, 'watchmap/watchmap_create.html',
                  {'random': '%d' % randrange(1000),
                   'authenticated': request.user.is_authenticated
                   })
