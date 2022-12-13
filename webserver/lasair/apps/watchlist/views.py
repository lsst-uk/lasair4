from .forms import WatchlistForm, UpdateWatchlistForm
import time
import random
import json
from subprocess import Popen, PIPE
from lasair.apps.watchlist.models import Watchlist, WatchlistCone
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from django.shortcuts import render, get_object_or_404, redirect
import src.run_crossmatch as run_crossmatch
import settings
from django.contrib import messages
from src import db_connect
import sys
from lasair.apps.db_schema.utils import get_schema_dict
from .utils import handle_uploaded_file, add_watchlist_metadata
sys.path.append('../common')


def watchlist_download(request, wl_id):
    """*download the original watchlist*

    **Key Arguments:**

    - `request` -- the original request
    - `wl_id` -- the watchlist catlaogue UUID

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchlists/<int:wl_id>/cat/', views.watchlist_download, name='watchlist_download'),
        ...
    ]
    ```
    """

    # GET THE WATCHLIST FROM DATABASE
    watchlist = get_object_or_404(Watchlist, wl_id=wl_id)

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    is_owner = (request.user.is_authenticated) and (request.user.id == watchlist.user.id)
    is_public = (watchlist.public == 1)
    is_visible = is_owner or is_public
    if not is_visible:
        messages.error(request, "This watchlist is private and not visible to you")
        return render(request, 'error.html')

    msl = db_connect.remote()

    s = []
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute('SELECT name FROM watchlists WHERE wl_id=%d' % wl_id)
    name = cursor.fetchall()[0]["name"].replace(" ", "_") + "_watchlist_original.csv"

    cursor.execute('SELECT ra, decl, name, radius FROM watchlist_cones WHERE wl_id=%d LIMIT 10000' % wl_id)
    cones = cursor.fetchall()
    content = []
    content[:] = [','.join(str(value) for value in c.values()) for c in cones]
    content = '\n'.join(content)

    response = HttpResponse(content, content_type='application/text charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{name}"'
    return response


def watchlist_detail(request, wl_id):
    """*return the resulting matches of a watchlist*

    **Key Arguments:**

    - `request` -- the original request
    - `wl_id` -- the watchlist catlaogue UUID

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchlists/<int:wl_id>/', views.watchlist_detail, name='watchlist_detail'),
        ...
    ]
    ```
    """

    msl = db_connect.remote()
    watchlist = get_object_or_404(Watchlist, wl_id=wl_id)

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    is_owner = (request.user.is_authenticated) and (request.user.id == watchlist.user.id)
    is_public = (watchlist.public == 1)
    is_visible = is_owner or is_public
    if not is_visible:
        messages.error(request, "This watchlist is private and not visible to you")
        return render(request, 'error.html')

    if request.method == 'POST' and is_owner:
        action = request.POST.get('action')
        # REQUEST TO UPDATE THE WATCHLIST DETAILS
        if action == 'save':
            watchlist.name = request.POST.get('name')
            watchlist.description = request.POST.get('description')

            if request.POST.get('active'):
                watchlist.active = 1
            else:
                watchlist.active = 0

            if request.POST.get('public'):
                watchlist.public = 1
            else:
                watchlist.public = 0

            watchlist.radius = float(request.POST.get('radius'))
            if watchlist.radius > 360:
                watchlist.radius = 360
            watchlist.save()
            messages.success(request, f'Your watchlist has been successfully updated')
        # REQUEST TO REFRESH THE WATCHLIST MATCHES
        elif action == 'run':
            hits = run_crossmatch.run_crossmatch(msl, watchlist.radius, watchlist.wl_id)
            messages.success(request, f'{hits} crossmatches found')

    # FIND THE COUNT OF WATCHLIST MATCHES
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute('SELECT count(*) AS count FROM watchlist_cones WHERE wl_id=%d' % wl_id)
    for row in cursor:
        number_cones = row['count']

    # GRAB ALL WATCHLIST MATCHES
    query_hit = """
SELECT
h.name as "Catalogue ID", h.arcsec as "separation (arcsec)",c.cone_id, o.objectId, o.ramean,o.decmean, o.rmag, o.gmag, jdnow()-o.jdmax as "last detected (days ago)"
FROM watchlist_cones AS c
NATURAL JOIN watchlist_hits as h
NATURAL JOIN objects AS o
WHERE c.wl_id=%d 
"""

    cursor.execute(query_hit % wl_id)
    hits = cursor.fetchall()

    # ADD SCHEMA
    schema = get_schema_dict("objects")
    if len(hits):
        for k in hits[0].keys():
            if k not in schema:
                schema[k] = "custom column"

    form = UpdateWatchlistForm(instance=watchlist)

    return render(request, 'watchlist/watchlist_detail.html', {
        'watchlist': watchlist,
        'conelist': hits,
        'count': len(hits),
        'number_cones': number_cones,
        'is_owner': is_owner,
        'schema': schema,
        'form': form})


@csrf_exempt
def watchlist_index(request):
    """*Return list of all watchlists viewable by user*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchlists/', views.watchlist_index, name='watchlist_index'),
        ...
    ]
    ```
    """

    # DELETE WATCHLIST -- NEEDS MOVE TO IT'S OWN FUNCTION
    if request.method == 'POST' and request.user.is_authenticated:
        delete = request.POST.get('delete')

        if delete == None:   # create new watchlist

            pass
        else:
            wl_id = int(delete)
            watchlist = get_object_or_404(Watchlist, wl_id=wl_id)
            if request.user == watchlist.user:
                # delete all the cones of this watchlist
                WatchlistCone.objects.filter(wl_id=wl_id).delete()
                # delete all the hits of this watchlist
                query = 'DELETE from watchlist_hits WHERE wl_id=%d' % wl_id
                msl = db_connect.remote()
                cursor = msl.cursor(buffered=True, dictionary=True)
                cursor.execute(query)
                msl.commit()
                # delete the watchlist
                watchlist.delete()
                messages.sucess(request, f'Watchlist {watchlist.name} deleted successfully')
            else:
                messages.error(request, f'Must be owner to delete watchlist')

    # PUBLIC WATCHLISTS
    publicWatchlists = Watchlist.objects.filter(public__gte=1)
    publicWatchlists = add_watchlist_metadata(publicWatchlists, remove_duplicates=True)

    # USER WATCHLISTS
    if request.user.is_authenticated:
        myWatchlists = Watchlist.objects.filter(user=request.user)
        myWatchlists = add_watchlist_metadata(myWatchlists)
    else:
        myWatchlists = None

    form = WatchlistForm()

    return render(request, 'watchlist/watchlist_index.html',
                  {'myWatchlists': myWatchlists,
                   'publicWatchlists': publicWatchlists,
                   'authenticated': request.user.is_authenticated,
                   'form': form})


def watchlist_create(request):
    """*create a new watchlist*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchlists/create/', views.watchlist_create, name='watchlist_create'),
        ...
    ]
    ```
    """

    # SUBMISSION OF NEW WATCHLIST
    if request.method == "POST" and request.user.is_authenticated:
        form = WatchlistForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            # GET WATCHLIST PARAMETERS
            t = time.time()
            name = request.POST.get('name')
            description = request.POST.get('description')
            d_radius = request.POST.get('radius')
            cones = request.POST.get('cones_textarea')
            if 'cones_file' in request.FILES:
                cones = handle_uploaded_file(request.FILES['cones_file'])
            try:
                default_radius = float(d_radius)
            except:
                messages.error(request, f'Cannot parse default radius {d_radius}')

            cone_list = []
            for line in cones.split('\n'):
                if len(line) == 0:
                    continue
                if line[0] == '#':
                    continue
                line = line.replace('|', ',')
                tok = line.split(',')
                if len(tok) < 2:
                    continue
                try:
                    if len(tok) >= 3:
                        ra = float(tok[0])
                        dec = float(tok[1])
                        objectId = tok[2].strip()
                        if len(tok) >= 4:
                            radius = float(tok[3])
                        else:
                            radius = None
                        cone_list.append([objectId, ra, dec, radius])
                except Exception as e:
                    messages.error(request, f'Bad line {len(cone_list)}: {line}\n{str(e)}')

            wl = Watchlist(user=request.user, name=name, description=description, active=0, radius=default_radius)
            wl.save()
            cones = []
            for cone in cone_list:
                name = cone[0].encode('ascii', 'ignore').decode()
                if name != cone[0]:
                    messages.info(request, 'Non-ascii characters removed from name %s --> %s<br/>' % (cone[0], name))
                wlc = WatchlistCone(wl=wl, name=name, ra=cone[1], decl=cone[2], radius=cone[3])
                cones.append(wlc)
            chunks = 1 + int(len(cones) / 50000)
            for i in range(chunks):
                WatchlistCone.objects.bulk_create(cones[(i * 50000): ((i + 1) * 50000)])

            watchlistname = form.cleaned_data.get('name')
            messages.success(request, f'The {watchlistname} catalogue watchlist has been successfully created')
            return redirect(f'watchlist_detail', wl.pk)
