from .models import Watchmap
import tempfile
import io

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
from lasair.apps.db_schema.utils import get_schema_dict
from src import db_connect
import sys
from .forms import WatchmapForm, UpdateWatchmapForm
from .utils import make_image_of_MOC, add_watchmap_metadata
from lasair.utils import bytes2string, string2bytes
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

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    is_owner = (request.user.is_authenticated) and (request.user.id == watchmap.user.id)
    is_public = (watchmap.public == 1)
    is_visible = is_owner or is_public
    if not is_visible:
        return render(request, 'error.html', {
            'message': "This watchmap is private and not visible to you"})

    moc = string2bytes(watchmap.moc)

    filename = slugify(watchmap.name) + '.fits'
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

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    is_owner = (request.user.is_authenticated) and (request.user.id == watchmap.user.id)
    is_public = (watchmap.public == 1)
    is_visible = is_owner or is_public
    if not is_visible:
        return render(request, 'error.html', {
            'message': "This watchmap is private and not visible to you"})

    if request.method == 'POST' and is_owner:
        if 'name' in request.POST:
            watchmap.name = request.POST.get('name')
            watchmap.description = request.POST.get('description')

            if request.POST.get('active'):
                watchmap.active = 1
            else:
                watchmap.active = 0

            if request.POST.get('public'):
                watchmap.public = 1
            else:
                watchmap.public = 0

            watchmap.save()
            message += 'watchmap updated'

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    # cursor.execute('SELECT count(*) AS count FROM area_hits WHERE ar_id=%d' % ar_id)
    # for row in cursor:
    #     count = row[0]

    query_hit = f"""
SELECT
o.objectId, o.ramean,o.decmean, o.rmag, o.gmag, jdnow()-o.jdmax as "last detected (days ago)"
FROM area_hits as h, objects AS o
WHERE h.ar_id={ar_id}
AND o.objectId=h.objectId
"""

    cursor.execute(query_hit)
    objectlist = cursor.fetchall()
    count = len(objectlist)

    schema = get_schema_dict("objects")

    if len(objectlist):
        for k in objectlist[0].keys():
            if k not in schema:
                schema[k] = "custom column"

    form = UpdateWatchmapForm(instance=watchmap)

    return render(request, 'watchmap/watchmap_detail.html', {
        'watchmap': watchmap,
        'objectlist': objectlist,
        'mocimage': watchmap.mocimage,
        'count': count,
        'is_owner': is_owner,
        'message': message,
        'schema': schema,
        'form': form})


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
    # SUBMISSION OF NEW WATCHLIST
    message = ""
    if request.method == "POST" and request.user.is_authenticated:
        form = WatchmapForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            # GET WATCHLIST PARAMETERS
            t = time.time()
            name = request.POST.get('name')
            description = request.POST.get('description')
            if 'mapfile' in request.FILES:
                mapfile = handle_uploaded_file(request.FILES['mapfile'])

            wl = Watchmaps(user=request.user, name=name, description=description, active=0, radius=default_radius)
            wl.save()
            cones = []
            for cone in cone_list:
                name = cone[0].encode('ascii', 'ignore').decode()
                if name != cone[0]:
                    message += 'Non-ascii characters removed from name %s --> %s<br/>' % (cone[0], name)
                wlc = WatchlistCone(wl=wl, name=name, ra=cone[1], decl=cone[2], radius=cone[3])
                cones.append(wlc)
            chunks = 1 + int(len(cones) / 50000)
            for i in range(chunks):
                WatchlistCone.objects.bulk_create(cones[(i * 50000): ((i + 1) * 50000)])

            watchlistname = form.cleaned_data.get('name')
            messages.success(request, f'The {watchlistname} catalogue watchlist has been successfully created')
            return redirect('watchlist_index')
    else:
        form = WatchmapForm()
    return render(request, 'watchmap/watchmap_create.html', {'form': form})
