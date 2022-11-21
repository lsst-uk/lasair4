from .forms import WatchlistForm, UpdateWatchlistForm
import time
import random
import json
from subprocess import Popen, PIPE
from lasair.apps.watchlist.models import Watchlists, WatchlistCones
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
        path('watchlists/create/', views.watchlist_create, name='watchlist_create'),
        ...
    ]
    ```
    """
    message = ''
    watchlist = get_object_or_404(Watchlists, wl_id=wl_id)

    is_owner = (request.user.is_authenticated) and (request.user == watchlist.user)
    is_public = (watchlist.public == 1)
    is_visible = is_owner or is_public
    if not is_visible:
        return render(request, 'error.html', {
            'message': "This watchlist is private and not visible to you"})
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
    message = ''
    watchlist = get_object_or_404(Watchlists, wl_id=wl_id)

    is_owner = (request.user.is_authenticated) and (request.user == watchlist.user)
    is_public = (watchlist.public == 1)
    is_visible = is_owner or is_public
    if not is_visible:
        return render(request, 'error.html', {
            'message': "This watchlist is private and not visible to you"})

    if request.method == 'POST' and is_owner:
        if 'name' in request.POST:
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
        else:
            msl = db_connect.remote()
            hits = run_crossmatch.run_crossmatch(msl, watchlist.radius, watchlist.wl_id)
            messages.success(request, f'{hits} crossmatches found')

    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute('SELECT count(*) AS count FROM watchlist_cones WHERE wl_id=%d' % wl_id)
    for row in cursor:
        number_cones = row['count']

    query_hit = """
SELECT
h.name as "Catalogue ID", h.arcsec as "separation (arcsec)",c.cone_id, o.objectId, o.ramean,o.decmean, o.rmag, o.gmag, jdnow()-o.jdmax as "last detected (days ago)"
FROM watchlist_cones AS c
NATURAL JOIN watchlist_hits as h
NATURAL JOIN objects AS o
WHERE c.wl_id=%d
"""
    query_nohit = """
SELECT
c.ra, c.decl, c.name, c.radius, c.cone_id
FROM watchlist_cones AS c
WHERE c.wl_id=%d LIMIT 100
"""
    cursor.execute(query_hit % wl_id)
    hits = cursor.fetchall()
    conelist = []
    coneIdList = []
    number_hits = len(hits)
    number_in_list = 0

    for c in hits:
        coneId = c["cone_id"]
        del c["cone_id"]

        coneIdList.append(coneId)
        conelist.append(c)
        number_in_list += 1
        if number_in_list >= 100:
            break

    # cursor.execute(query_nohit % wl_id)
    # cones = cursor.fetchall()
    # for c in cones:
    #     coneId = c["cone_id"]
    #     del c["cone_id"]

    #     if not c['radius']:
    #         c['radius'] = watchlist.radius
    #     if coneId not in coneIdList:
    #         number_in_list += 1
    #         if number_in_list >= 100:
    #             break
    #         conelist.append(c)

    count = len(conelist)

    schema = get_schema_dict("objects")

    if len(conelist):
        for k in conelist[0].keys():
            if k not in schema:
                schema[k] = "custom column"

    form = UpdateWatchlistForm(instance=watchlist)

    return render(request, 'watchlist/watchlist_detail.html', {
        'watchlist': watchlist,
        'conelist': conelist,
        'count': len(conelist),
        'number_cones': number_cones,
        'number_hits': number_hits,
        'is_owner': is_owner,
        'message': message,
        'schema': schema,
        'form': form})


@ csrf_exempt
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
    message = ''
    if request.method == 'POST' and request.user.is_authenticated:
        delete = request.POST.get('delete')

        if delete == None:   # create new watchlist

            pass
        else:
            wl_id = int(delete)
            watchlist = get_object_or_404(Watchlists, wl_id=wl_id)
            if request.user == watchlist.user:
                # delete all the cones of this watchlist
                WatchlistCones.objects.filter(wl_id=wl_id).delete()
                # delete all the hits of this watchlist
                query = 'DELETE from watchlist_hits WHERE wl_id=%d' % wl_id
                msl = db_connect.remote()
                cursor = msl.cursor(buffered=True, dictionary=True)
                cursor.execute(query)
                msl.commit()
                # delete the watchlist
                watchlist.delete()
                message = 'Watchlist %s deleted successfully' % watchlist.name
            else:
                message = 'Must be owner to delete watchlist'

    # public watchlists belong to the anonymous user
    other_watchlists = Watchlists.objects.filter(public__gte=1)
    other_watchlists = add_watchlist_metadata(other_watchlists, remove_duplicates=True)

    if request.user.is_authenticated:
        my_watchlists = Watchlists.objects.filter(user=request.user)
        my_watchlists = add_watchlist_metadata(my_watchlists)
    else:
        my_watchlists = None

    return render(request, 'watchlist/watchlist_index.html',
                  {'my_watchlists': my_watchlists,
                   'random': '%d' % random.randrange(1000),
                   'other_watchlists': other_watchlists,
                   'authenticated': request.user.is_authenticated,
                   'message': message})


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
    message = ""
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
                message += 'Cannot parse default radius %s\n' % d_radius

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
                    message += "Bad line %d: %s<br/>" % (len(cone_list), line)
                    message += str(e)
            wl = Watchlists(user=request.user, name=name, description=description, active=0, radius=default_radius)
            wl.save()
            cones = []
            for cone in cone_list:
                name = cone[0].encode('ascii', 'ignore').decode()
                if name != cone[0]:
                    message += 'Non-ascii characters removed from name %s --> %s<br/>' % (cone[0], name)
                wlc = WatchlistCones(wl=wl, name=name, ra=cone[1], decl=cone[2], radius=cone[3])
                cones.append(wlc)
            chunks = 1 + int(len(cones) / 50000)
            for i in range(chunks):
                WatchlistCones.objects.bulk_create(cones[(i * 50000): ((i + 1) * 50000)])

            watchlistname = form.cleaned_data.get('name')
            messages.success(request, f'The {watchlistname} catalogue watchlist has been successfully created')
            return redirect('watchlist_index')
    else:
        form = WatchlistForm()
    return render(request, 'watchlist/watchlist_create.html', {'form': form})

    # return render(request, 'watchlist/watchlist_create.html',
    #               {'random': '%d' % random.randrange(1000),
    #                'authenticated': request.user.is_authenticated
    #                })
