from .utils import add_filter_query_metadata, run_filter, topic_name, check_query_zero_limit, delete_stream_file
import random
from src import date_nid, db_connect
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from lasair.apps.annotator.models import Annotators
from lasair.apps.watchmap.models import Watchmap
from lasair.apps.watchlist.models import Watchlist
from confluent_kafka import Producer, KafkaError, admin
from django.views.decorators.csrf import csrf_exempt
from lasair.apps.db_schema.utils import get_schema, get_schema_dict, get_schema_for_query_selected
from .models import filter_query
from .forms import filterQueryForm, UpdateFilterQueryForm
from lasair.query_builder import check_query, build_query
import settings
import json
import re
import time
from datetime import datetime
from django.contrib import messages
import os
import sys
import sqlparse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
sys.path.append('../common')


@csrf_exempt
def filter_query_index(request):
    """*Return list of all filter queries viewable by user*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('filters/', views.filter_query_index, name='filter_query_index'),
        ...
    ]
    ```
    """

    # PUBLIC FILTERS
    publicFilters = filter_query.objects.filter(public__gte=1)
    publicFilters = add_filter_query_metadata(publicFilters, remove_duplicates=True)

    # USER FILTERS
    if request.user.is_authenticated:
        myFilters = filter_query.objects.filter(user=request.user)
        myFilters = add_filter_query_metadata(myFilters)
    else:
        myFilters = None

    return render(request, 'filter_query/filter_query_index.html',
                  {'myFilters': myFilters,
                   'publicFilters': publicFilters,
                   'authenticated': request.user.is_authenticated})


def filter_query_detail(request, mq_id):
    """*return the result of a filter query*

    **Key Arguments:**

    - `request` -- the original request
    - `mq_id` -- the filter UUID

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('filters/<int:mq_id>/', views.filter_query_detail, name='filter_query_detail'),
        ...
    ]
    ```
    """

    # CONNECT TO DATABASE AND GET FILTER
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    filterQuery = get_object_or_404(filter_query, mq_id=mq_id)

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    is_owner = (request.user.is_authenticated) and (request.user.id == filterQuery.user.id)
    is_public = (filterQuery.public == 1)
    is_visible = is_owner or is_public
    if not is_visible:
        messages.error(request, "This filter is private and not visible to you")
        return render(request, 'error.html')

    if request.method == 'POST' and is_owner:
        # UPDATING SETTINGS?
        filterQuery.name = request.POST.get('name')
        filterQuery.description = request.POST.get('description')

        if request.POST.get('active'):
            filterQuery.active = int(request.POST.get('active'))
        else:
            filterQuery.active = 0

        if request.POST.get('public'):
            filterQuery.public = 1
        else:
            filterQuery.public = 0

        # VERIFY QUERY WORKS
        e = check_query(filterQuery.selected, filterQuery.tables, filterQuery.conditions)
        if e:
            messages.error(request, f"There was an error updating your filter.\n{e}")
            return render(request, 'error.html')
        filterQuery.real_sql = build_query(filterQuery.selected, filterQuery.tables, filterQuery.conditions)
        e = check_query_zero_limit(filterQuery.real_sql)
        if e:
            messages.error(request, f"There was an error updating your filter.\n{e}")
            return render(request, 'error.html')

        # REFRESH STREAM
        tn = topic_name(request.user.id, filterQuery.name)
        filterQuery.topic_name = tn
        delete_stream_file(request, filterQuery.name)
        if filterQuery.active == 2:
            try:
                topic_refresh(filterQuery.real_sql, tn, limit=10)
            except Exception as e:
                messages.error(request, f'The kafa topic could not be refreshed for this filter. {e}')
        filterQuery.save()
        messages.success(request, f'Your filter has been successfully updated')

    cursor.execute(f'SELECT name, selected, tables, conditions, real_sql FROM myqueries WHERE mq_id={mq_id}')
    for row in cursor:
        query_name = row['name']
        selected = row['selected']
        tables = row['tables']
        conditions = row['conditions']
        real_sql = row['real_sql']
        filterQuery.real_sql = sqlparse.format(filterQuery.real_sql, reindent=True, keyword_case='upper', strip_comments=True)

    limit = 5000
    offset = 0

    form = UpdateFilterQueryForm(instance=filterQuery)

    table, schema, count, topic, error = run_filter(
        selected=filterQuery.selected,
        tables=filterQuery.tables,
        conditions=filterQuery.conditions,
        limit=limit,
        offset=offset,
        mq_id=mq_id,
        query_name=filterQuery.name)

    if count > limit:
        if settings.DEBUG:
            apiUrl = "https://lasair.readthedocs.io/en/develop/core_functions/rest-api.html"
        else:
            apiUrl = "https://lasair.readthedocs.io/en/main/core_functions/rest-api.html"
        messages.info(request, f"We are only displaying the first <b>{limit}</b> of {count} objects matched against this filter. But don't worry! You can access all {count} results via the <a class='alert-link' href='{apiUrl}' target='_blank'>Lasair API</a>.")
    else:
        limit = False

    if error:
        messages.error(request, error)

    return render(request, 'filter_query/filter_query_detail.html', {
        'filterQ': filterQuery,
        'table': table,
        'count': count,
        "schema": schema,
        "form": form,
        'limit': str(limit)
    })


@login_required
def filter_query_create(request):
    """*create a new filter*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('filters/create/', views.filter_query_create, name='filter_create'),
        ...
    ]
    ```
    """

    # BUILD CONTENT FOR THE CREATION FORM
    schemas_core = {
        'objects': get_schema('objects'),
        'sherlock_classifications': get_schema('sherlock_classifications')
    }
    schemas_addtional = {
        'watchlist_hits': get_schema('watchlist_hits'),
        'annotations': get_schema('annotations'),
    }
    form = filterQueryForm(request.POST, request.FILES, request=request)
    email = request.user.email
    watchlists = Watchlist.objects.filter(Q(user=request.user) | Q(public__gte=1))
    watchmaps = Watchmap.objects.filter(Q(user=request.user) | Q(public__gte=1))
    annotators = Annotators.objects.filter(Q(user=request.user) | Q(public__gte=1))

    # SUBMISSION OF NEW FILTER - EITHER SIMPLE RUN OR SAVE
    if request.method == 'POST':

        # COLLECT FORM CONTENT
        action = request.POST.get('action')
        selected = request.POST.get('selected')
        conditions = request.POST.get('conditions')
        watchlists = request.POST.get('watchlists')
        watchmaps = request.POST.getlist('watchmaps')
        annotators = request.POST.getlist('annotators')
        name = request.POST.get('name')
        description = request.POST.get('description')
        if request.POST.get('public'):
            public = 1
        else:
            public = 0
        active = request.POST.get('active')

        # EXTRA DEFAULTS
        tables = "objects"
        limit = 1000
        offset = 0

        # FIND THE TABLES THAT NEED TO BE QUIERIED FROM THE SELECT STATEMENT
        matchObjectList = re.findall(r'([a-zA-Z0-9_\-]*)\.([a-zA-Z0-9_\-]*)', selected)
        tables = [m[0] for m in matchObjectList]
        tables = (",").join(set(tables))
        if watchlists:
            tables += f", watchlist:{watchlists}"
        if watchmaps:
            tables += f", area:{('&').join(watchmaps)}"
        if annotators:
            tables += f", annotator:{('&').join(annotators)}"

        # RUN?
        if action and action.lower() == "run":

            table, tableSchema, nalert, topic, error = run_filter(
                selected=selected,
                tables=tables,
                conditions=conditions,
                limit=limit,
                offset=offset,
                mq_id=None,
                query_name=False)

            if error:
                messages.error(request, error)

            sqlquery_real = sqlparse.format(build_query(selected, tables, conditions), reindent=True, keyword_case='upper', strip_comments=True)

            return render(request, 'filter_query/filter_query_create.html', {'schemas_core': schemas_core, 'schemas_addtional': schemas_addtional, 'form': form, 'table': table, 'schema': tableSchema, 'limit': str(limit), 'real_sql': sqlquery_real})

        # OR SAVE?
        elif action and action.lower() == "save" and len(name):

            if form.is_valid():
                e = check_query(selected, tables, conditions)
                if e:
                    return render(request, 'error.html', {'message': e})

                sqlquery_real = build_query(selected, tables, conditions)
                e = check_query_zero_limit(sqlquery_real)
                if e:
                    return render(request, 'error.html', {'message': e})

                tn = topic_name(request.user.id, name)

                mq = filter_query(user=request.user,
                                  name=name, description=description,
                                  public=public, active=active,
                                  selected=selected, conditions=conditions, tables=tables,
                                  real_sql=sqlquery_real, topic_name=tn)

                mq.save()

                # AFTER SAVING, DELETE THE TOPIC AND PUSH SOME RECORDS FROM THE DATABASE
                if mq.active == 2:
                    message.success(request, topic_refresh(mq.real_sql, tn, limit=10))

                filtername = form.cleaned_data.get('name')
                messages.success(request, f'The "{filtername}" filter has been successfully created')
                return redirect(f'filter_query_detail', mq.pk)

    return render(request, 'filter_query/filter_query_create.html', {'schemas_core': schemas_core, 'schemas_additional': schemas_addtional, 'form': form, 'limit': None})


def filter_log(request, topic):
    """*return the log file content for the filter*

    **Key Arguments:**

    - `request` -- the original request
    - `topic` -- the name of the filter topic

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('filters/log/<slug:topic>/', views.filter_log, name='filter_log'),
        ...
    ]
    ```
    """
    try:
        data = open(settings.KAFKA_STREAMS + '/' + topic, 'r').read()
    except:
        messages.error(request, f'Cannot find log file for {topic}.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # GRAB TABLE FROM FILE
    table = json.loads(data)['digest']
    count = len(table)

    # GRAB MQ ID FROM FILENAME
    regex = re.compile(r'lasair_(\d*)')
    title = regex.sub("", topic, count=1)
    topicUserId = int(topic.replace('lasair_', '').replace(title, ''))
    filterQuery = filter_query.objects.filter(Q(topic_name=topic))
    if len(filterQuery):
        filterQuery = filterQuery[0]
    else:
        messages.error(request, f"Filter does not exist for topic '{topic}'.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # VERIFY USER ALLOWED TO VIEW
    if not filterQuery.public and filterQuery.user.id != request.user.id:
        messages.error(request, "This filter is private and not visible to you")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    form = UpdateFilterQueryForm(instance=filterQuery)

    tableSchema = get_schema_for_query_selected(filterQuery.selected)
    for k in table[0].keys():
        if k not in tableSchema:
            tableSchema[k] = "custom column"

    return render(request, 'filter_query/filter_query_detail.html', {
        'filterQ': filterQuery,
        'table': table,
        'count': count,
        "schema": tableSchema,
        "form": form,
        'limit': None
    })


@login_required
def filter_query_delete(request, mq_id):
    """*delete a filter query*

    **Key Arguments:**

    - `request` -- the original request
    - `mq_id` -- the filter UUID

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('filters/<int:mq_id>/delete/', views.filter_query_delete, name='filter_query_delete'),
        ...
    ]
    ```
    """
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    print(mq_id)
    filterQuery = get_object_or_404(filter_query, mq_id=mq_id)
    print(filterQuery)
    name = filterQuery.name

    # DELETE FILTER
    if request.method == 'POST' and request.user.is_authenticated and filterQuery.user.id == request.user.id and request.POST.get('action') == "delete":
        filterQuery.delete()
        delete_stream_file(request, filterQuery.name)
        messages.success(request, f'The "{name}" filter has been successfully deleted')
    else:
        messages.error(request, f'You must be the owner to delete this filter')
    return redirect('filter_query_index')


@login_required
def filter_query_duplicate(request, mq_id):
    """*duplicate a filter query*

    **Key Arguments:**

    - `request` -- the original request
    - `mq_id` -- the filter UUID

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('filters/<int:mq_id>/duplicate/', views.filter_query_duplicate, name='filter_query_duplicate'),
        ...
    ]
    ```
    """
    # msl = db_connect.readonly()
    # cursor = msl.cursor(buffered=True, dictionary=True)
    # print(mq_id)
    # filterQuery = get_object_or_404(filter_query, mq_id=mq_id)
    # print(filterQuery)
    # name = filterQuery.name

    # # DELETE FILTER
    # if request.method == 'POST' and request.user.is_authenticated and filterQuery.user.id == request.user.id and request.POST.get('action') == "delete":
    #     filterQuery.delete()
    #     delete_stream_file(request, filterQuery.name)
    #     messages.success(request, f'The "{name}" filter has been successfully deleted')
    # else:
    #     messages.error(request, f'You must be the owner to delete this filter')
    return redirect('filter_query_index')
