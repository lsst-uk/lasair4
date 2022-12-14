from .utils import add_filter_query_metadata, run_filter, topic_name
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
    message = ''

    # public watchlists belong to the anonymous user
    other_filter_queries = filter_query.objects.filter(public__gte=1)
    other_filter_queries = add_filter_query_metadata(other_filter_queries, remove_duplicates=True)

    if request.user.is_authenticated:
        my_filter_queries = filter_query.objects.filter(user=request.user)
        my_filter_queries = add_filter_query_metadata(my_filter_queries)
    else:
        my_filter_queries = None

    return render(request, 'filter_query/filter_query_index.html',
                  {'my_filter_queries': my_filter_queries,
                   'random': '%d' % random.randrange(1000),
                   'other_filter_queries': other_filter_queries,
                   'authenticated': request.user.is_authenticated,
                   'message': message})


def filter_log(request, topic):
    """stream.

    Args:
        request:
        topic:
    """
    try:
        data = open(settings.KAFKA_STREAMS + '/' + topic, 'r').read()
    except:
        return render(request, 'error.html', {'message': f'Cannot find log file for {topic}.'})
    table = json.loads(data)['digest'][:100]
    nalert = len(table)

    regex = re.compile(r'lasair_(\d*)')
    title = regex.sub("", topic, count=1)
    mq_id = int(topic.replace('lasair_', '').replace(title, ''))

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute('SELECT name, selected, tables, conditions FROM myqueries WHERE mq_id=%d' % mq_id)
    for row in cursor:
        title = row['name']
        selected = row['selected']
        tables = row['tables']
        conditions = row['conditions']

    tableSchema = get_schema_for_query_selected(selected)
    for k in table[0].keys():
        if k not in tableSchema:
            tableSchema[k] = "custom column"

    return render(request, 'filter_query/filter_query_detail.html', {'topic': topic, 'nalert': nalert, 'table': table, 'mq_id': mq_id, 'title': title, "schema": tableSchema})


def handle_myquery(request, mq_id=None):
    """handle_myquery.

    Args:
        request:
        mq_id:
    """
    logged_in = request.user.is_authenticated
    message = ''

    schemas = {
        'objects': get_schema('objects'),
        'sherlock_classifications': get_schema('sherlock_classifications'),
        'crossmatch_tns': get_schema('crossmatch_tns'),
        'annotations': get_schema('annotations'),
    }

    if logged_in:
        email = request.user.email
        watchlists = Watchlist.objects.filter(Q(user=request.user) | Q(public__gte=1))
        watchmaps = Watchmap.objects.filter(Q(user=request.user) | Q(public__gte=1))
        annotators = Annotators.objects.filter(Q(user=request.user) | Q(public__gte=1))
    else:
        email = ''
        watchlists = Watchlist.objects.filter(public__gte=1)
        watchmaps = Watchmap.objects.filter(public__gte=1)
        annotators = Annotators.objects.filter(public__gte=1)

    if mq_id is None:
        # New query, returned from form
        if request.method == 'POST' and logged_in:
            name = request.POST.get('name')
            description = request.POST.get('description')
            selected = request.POST.get('selected')
            conditions = request.POST.get('conditions')
            tables = request.POST.get('tables')
            try:
                active = int(request.POST.get('active'))
            except:
                active = 0

            public = request.POST.get('public')
            if public == 'on':
                public = 1
            else:
                public = 0

            e = check_query(selected, tables, conditions)
            if e:
                return render(request, 'error.html', {'message': e})

            sqlquery_real = build_query(selected, tables, conditions)
            e = check_query_zero_limit(sqlquery_real)
            if e:
                return render(request, 'error.html', {'message': e})

            tn = topic_name(request.user.id, name)

            myquery = filter_query(user=request.user,
                                   name=name, description=description,
                                   public=public, active=active,
                                   selected=selected, conditions=conditions, tables=tables,
                                   real_sql=sqlquery_real, topic_name=tn)
            myquery.save()

            # after saving, delete the topic and push some records from the database
            if myquery.active == 2:
                message += topic_refresh(myquery.real_sql, tn, limit=10)

            message += "Query saved successfully"
            return render(request, 'queryform.html', {
                'myquery': myquery,
                'watchlists': watchlists,
                'watchmaps': watchmaps,
                'annotators': annotators,
                'topic': tn,
                'is_owner': True,
                'logged_in': logged_in,
                'email': email,
                'new': False,
                'newandloggedin': False,
                'schemas': schemas,
                'message': message})
        else:
            # New query, blank query form
            message += 'New query'
            return render(request, 'queryform.html', {
                'watchlists': watchlists,
                'watchmaps': watchmaps,
                'annotators': annotators,
                'random': '%d' % random.randrange(1000),
                'email': email,
                'is_owner': False,
                'logged_in': logged_in,
                'email': email,
                'new': True,
                'newandloggedin': logged_in,
                'schemas': schemas,
                'message': message,
            })

    # EXISTING QUERY
    myquery = get_object_or_404(filter_query, mq_id=mq_id)

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    is_owner = logged_in and (request.user.id == myquery.user.id)
    if not is_owner and myquery.public == 0:
        return render(request, 'error.html', {'message': 'This query is private'})

    # Existing query, owner wants to change it
    if request.method == 'POST' and logged_in:

        #        s = ''   ####
        #        for k,v in request.POST.items():
        #            s += '%s --> %s<br/>' % (k,v)
        #        return render(request, 'error.html', {'message': s})

        # Delete the given query
        if 'delete' in request.POST:
            myquery.delete()
            delete_stream_file(request, myquery.name)
            return redirect('/explore')

        # Copy the given query
        if 'copy' in request.POST:
            newname = 'Copy_Of_' + myquery.name + '_'
            letters = string.ascii_lowercase
            newname += ''.join(random.choice(letters) for i in range(6))
            tn = topic_name(request.user.id, newname)
            mq = filter_query(user=request.user, name=newname,
                              description=myquery.description,
                              public=0, active=0,
                              selected=myquery.selected,
                              conditions=myquery.conditions, tables=myquery.tables,
                              real_sql=myquery.real_sql, topic_name=tn)
            mq.save()

            # after saving, delete the topic and push some records from the database
            if myquery.active == 2:
                message + topic_refresh(myquery.real_sql, tn, limit=10)

            message += 'Query copied<br/>'
            return redirect('/query/%d/' % mq.mq_id)

        # Update the given query from the post
        else:
            myquery.name = request.POST.get('name')
            myquery.description = request.POST.get('description')
            myquery.selected = request.POST.get('selected')
            myquery.tables = request.POST.get('tables')
            myquery.conditions = request.POST.get('conditions')
            public = request.POST.get('public')
            e = check_query(myquery.selected, myquery.tables, myquery.conditions)
            if e:
                return render(request, 'error.html', {'message': str(e) + '<br/>'})

            myquery.real_sql = build_query(myquery.selected, myquery.tables, myquery.conditions)
            e = check_query_zero_limit(myquery.real_sql)
            if e:
                return render(request, 'error.html', {'message': str(e) + '<br/>'})

            tn = topic_name(request.user.id, myquery.name)
            myquery.topic_name = tn
            try:
                myquery.active = int(request.POST.get('active'))
            except:
                myquery.active = 0

            if public == 'on':
                if myquery.public is None or myquery.public == 0:
                    myquery.public = 1  # if set to 1 or 2 leave it as it is
            else:
                myquery.public = 0
            delete_stream_file(request, myquery.name)

            # after saving, delete the topic and push some records from the database
            if myquery.active == 2:
                message += topic_refresh(myquery.real_sql, tn, limit=10)

            message += 'Query %s updated<br/>' % myquery.name

        myquery.save()
        return render(request, 'queryform.html', {
            'myquery': myquery,
            'watchlists': watchlists,
            'watchmaps': watchmaps,
            'annotators': annotators,
            'topic': tn,
            'is_owner': is_owner,
            'logged_in': logged_in,
            'email': email,
            'new': False,
            'newandloggedin': False,
            'schemas': schemas,
            'message': message})

    # Existing query, view it
    return render(request, 'queryform.html', {
        'myquery': myquery,
        'watchlists': watchlists,
        'watchmaps': watchmaps,
        'annotators': annotators,
        'topic': myquery.topic_name,
        'is_owner': is_owner,
        'logged_in': logged_in,
        'email': email,
        'new': False,
        'newandloggedin': False,
        'schemas': schemas,
        'message': message})


def querylist(request, which):
    """querylist.

    Args:
        request:
        which: can be 'promoted', 'pubic', 'my'
    """
    # shows the list of queries
    if request.user.is_authenticated:
        myqueries = filter_query.objects.filter(user=request.user)
    else:
        myqueries = None

    if request.user.is_authenticated:
        watchlists = Watchlist.objects.filter(Q(user=request.user) | Q(public__gte=1))
        watchmaps = Watchmap.objects.filter(Q(user=request.user) | Q(public__gte=1))
        annotators = Annotators.objects.filter(Q(user=request.user) | Q(public__gte=1))
    else:
        watchlists = Watchlist.objects.filter(public__gte=1)
        watchmaps = Watchmap.objects.filter(public__gte=1)
        annotators = Annotators.objects.filter(public__gte=1)

    promoted_queries = filter_query.objects.filter(public=2)
    public_queries = filter_query.objects.filter(public__gte=1)

    return render(request, 'querylist.html', {
        'which': which,
        'promoted_queries': query_list(promoted_queries),
        'is_authenticated': request.user.is_authenticated,
        'myqueries': query_list(myqueries),
        'watchlists': watchlists,
        'watchmaps': watchmaps,
        'annotators': annotators,
        'public_queries': query_list(public_queries)
    })


def query_list(qs):
    """query_list.

    Args:
        qs:
    """
    # takes the list of queries and adds a strealink for each one
    list = []
    if not qs:
        return list
    for q in qs:
        d = {
            'mq_id': q.mq_id,
            'usersname': q.user.first_name + ' ' + q.user.last_name,
            'selected': q.selected,
            'tables': q.tables,
            'conditions': q.conditions,
            'name': q.name,
            'active': q.active,
            'public': q.public,
            'description': q.description
        }
        d['streamlink'] = 'inactive'
        if q.active:
            topic = topic_name(q.user.id, q.name)
            d['streamlink'] = '/streams/%s' % topic
        list.append(d)
    return list


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
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute('SELECT name, selected, tables, conditions, real_sql FROM myqueries WHERE mq_id=%d' % mq_id)
    for row in cursor:
        query_name = row['name']
        selected = row['selected']
        tables = row['tables']
        conditions = row['conditions']
        real_sql = row['real_sql']
        import sqlparse
        real_sql = sqlparse.format(real_sql, reindent=True, keyword_case='upper', strip_comments=True)

    limit = 1000
    offset = 0
    json_checked = False

    thisFilter = get_object_or_404(filter_query, mq_id=mq_id)
    form = UpdateFilterQueryForm(request.POST, request.FILES, request=request, instance=thisFilter)

    message = ""

    table, tableSchema, nalert, topic, error = run_filter(
        selected=selected,
        tables=tables,
        conditions=conditions,
        limit=limit,
        offset=offset,
        mq_id=mq_id,
        query_name=query_name)

    if error:
        messages.error(request, error)

    if json_checked:
        return HttpResponse(json.dumps(table, indent=2), content_type="application/json")
    else:
        return render(request, 'filter_query/filter_query_detail.html',
                      {'table': table, 'nalert': nalert,
                       'topic': topic,
                       'title': query_name,
                       'mq_id': mq_id,
                       'selected': selected,
                       'tables': tables,
                       'conditions': conditions,
                       'nalert': nalert,
                       'ps': offset, 'pe': offset + nalert,
                       'limit': str(limit), 'offset': offset,
                       'message': real_sql,
                       "schema": tableSchema,
                       "form": form,
                       'filterQ': thisFilter})


def record_query(request, query):
    """record_query.

    Args:
        request:
        query:
    """
    onelinequery = query.replace('\r', ' ').replace('\n', ' ')
    time = datetime.now().replace(microsecond=0).isoformat()

    if request.user.is_authenticated:
        name = request.user.first_name + ' ' + request.user.last_name
    else:
        name = 'anonymous'

    IP = request.META.get('REMOTE_ADDR')
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        IP = record.request.META['HTTP_X_FORWARDED_FOR']

    date = date_nid.nid_to_date(date_nid.nid_now())
    filename = settings.QUERY_CACHE + '/' + date
    f = open(filename, 'a')
    s = '%s| %s| %s| %s\n' % (IP, name, time, onelinequery)
    f.write(s)
    f.close()


def check_query_zero_limit(real_sql):
    """*summary of function*

    **Key Arguments:**

    - `XXXXX` -- xxxx

    **Usage:**

    ```python
    usage code
    ```
    """
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)

    try:
        cursor.execute(real_sql + ' LIMIT 0')
        return None
    except Exception as e:
        message = 'Your query:<br/><b>' + real_sql + '</b><br/>returned the error<br/><i>' + str(e) + '</i>'
        return message


def delete_stream_file(request, query_name):
    topic = topic_name(request.user.id, query_name)
    filename = settings.KAFKA_STREAMS + topic
    if os.path.exists(filename):
        os.remove(filename)


def datetime_converter(o):
    # used by json encoder when it gets a type it doesn't understand
    if isinstance(o, datetime):
        return o.__str__()


def topic_refresh(real_sql, topic, limit=10):
    message = ''
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = real_sql + ' LIMIT %d' % limit

    try:
        cursor.execute(query)
    except Exception as e:
        message += 'Your query:<br/><b>' + query + '</b><br/>returned the error<br/><i>' + str(e) + '</i><br/>'
        return message

    recent = []
    for record in cursor:
        recorddict = dict(record)
        now_number = datetime.utcnow()
        recorddict['UTC'] = now_number.strftime("%Y-%m-%d %H:%M:%S")
        print(recorddict)
        recent.append(recorddict)

    conf = {
        'bootstrap.servers': settings.PUBLIC_KAFKA_SERVER,
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanisms': 'SCRAM-SHA-256',
        'sasl.username': 'admin',
        'sasl.password': settings.PUBLIC_KAFKA_PASSWORD
    }

    # delete the old topic
    a = admin.AdminClient(conf)

    try:
        result = a.delete_topics([topic])
        result[topic].result()
        time.sleep(1)
        message += 'Topic %s deleted<br/>' % topic
    except Exception as e:
        message += 'Topic is ' + topic + '<br/>'
        message += str(e) + '<br/>'

    # pushing in new messages will remake the topic
    try:
        p = Producer(conf)
        for out in recent:
            jsonout = json.dumps(out, default=datetime_converter)
            p.produce(topic, value=jsonout)
        p.flush(10.0)   # 10 second timeout
        message += '%d new messages produced to topic %s<br/>' % (limit, topic)
    except Exception as e:
        message += "ERROR in queries/topic_refresh: cannot produce to public kafka<br/>" + str(e) + '<br/>'
    return message


def filter_query_create(request, mq_id=None):
    """create a new filter.

    Args:
        request:
        mq_id:
    """
    logged_in = request.user.is_authenticated

    schemas = {
        'objects': get_schema('objects'),
        'sherlock_classifications': get_schema('sherlock_classifications'),
        'crossmatch_tns': get_schema('crossmatch_tns'),
        'annotations': get_schema('annotations'),
    }

    form = filterQueryForm(request.POST, request.FILES, request=request)

    if logged_in:
        email = request.user.email
        watchlists = Watchlist.objects.filter(Q(user=request.user) | Q(public__gte=1))
        watchmaps = Watchmap.objects.filter(Q(user=request.user) | Q(public__gte=1))
        annotators = Annotators.objects.filter(Q(user=request.user) | Q(public__gte=1))
    else:
        email = ''
        watchlists = Watchlist.objects.filter(public__gte=1)
        watchmaps = Watchmap.objects.filter(public__gte=1)
        annotators = Annotators.objects.filter(public__gte=1)

    if request.method == 'POST':

        action = request.POST.get('action')
        selected = request.POST.get('selected')
        conditions = request.POST.get('conditions')
        watchlists = request.POST.get('watchlists')
        watchmaps = request.POST.get('watchmaps')
        annotators = request.POST.get('annotators')

        tables = "objects"
        limit = 1000
        offset = 0
        name = request.POST.get('name')
        description = request.POST.get('description')
        public = request.POST.get('public')
        if public == 'on':
            public = 1
        else:
            public = 0

        active = 1

        # FIND THE TABLES THAT NEED TO BE QUIERIED FROM THE SELECT STATEMENT
        matchObjectList = re.findall(r'([a-zA-Z0-9_\-]*)\.([a-zA-Z0-9_\-]*)', selected)
        tables = [m[0] for m in matchObjectList]
        tables = (",").join(set(tables))
        if watchlists:
            tables += f", watchlist:{watchlists}"
        if watchmaps:
            tables += f", area:{watchmaps}"
        if annotators:
            tables += f", annotator:{annotators}"

        # RUN OR SAVE?
        if action and action.lower() == "run":

            table, tableSchema, nalert, topic, error = run_filter(
                selected=selected,
                tables=tables,
                conditions=conditions,
                limit=limit,
                offset=offset,
                mq_id=mq_id,
                query_name=False)

            if error:
                messages.error(request, error)

            return render(request, 'filter_query/filter_query_create.html', {'schemas': schemas, 'form': form, 'table': table, 'schema': tableSchema, 'limit': str(limit)})

        elif action and action.lower() == "save" and len(name):

            e = check_query(selected, tables, conditions)
            if e:
                return render(request, 'error.html', {'message': e})

            sqlquery_real = build_query(selected, tables, conditions)
            e = check_query_zero_limit(sqlquery_real)
            if e:
                return render(request, 'error.html', {'message': e})

            tn = topic_name(request.user.id, name)

            myquery = filter_query(user=request.user,
                                   name=name, description=description,
                                   public=public, active=active,
                                   selected=selected, conditions=conditions, tables=tables,
                                   real_sql=sqlquery_real, topic_name=tn)

            myquery.save()

            messages.success(request, f'The "{name}" filter has been successfully created')
            return redirect('filter_query_index')

    return render(request, 'filter_query/filter_query_create.html', {'schemas': schemas, 'form': form, 'limit': str(1000)})

    message = ''

    if logged_in:
        email = request.user.email
        watchlists = Watchlist.objects.filter(Q(user=request.user) | Q(public__gte=1))
        watchmaps = Watchmap.objects.filter(Q(user=request.user) | Q(public__gte=1))
        annotators = Annotators.objects.filter(Q(user=request.user) | Q(public__gte=1))
    else:
        email = ''
        watchlists = Watchlist.objects.filter(public__gte=1)
        watchmaps = Watchmap.objects.filter(public__gte=1)
        annotators = Annotators.objects.filter(public__gte=1)

    if mq_id is None:
        # New query, returned from form
        if request.method == 'POST' and logged_in:
            name = request.POST.get('name')
            description = request.POST.get('description')
            selected = request.POST.get('selected')
            conditions = request.POST.get('conditions')
            tables = request.POST.get('tables')
            try:
                active = int(request.POST.get('active'))
            except:
                active = 0

            public = request.POST.get('public')
            if public == 'on':
                public = 1
            else:
                public = 0

            e = check_query(selected, tables, conditions)
            if e:
                return render(request, 'error.html', {'message': e})

            sqlquery_real = build_query(selected, tables, conditions)
            e = check_query_zero_limit(sqlquery_real)
            if e:
                return render(request, 'error.html', {'message': e})

            tn = topic_name(request.user.id, name)

            myquery = filter_query(user=request.user,
                                   name=name, description=description,
                                   public=public, active=active,
                                   selected=selected, conditions=conditions, tables=tables,
                                   real_sql=sqlquery_real, topic_name=tn)
            myquery.save()

            # after saving, delete the topic and push some records from the database
            if myquery.active == 2:
                message += topic_refresh(myquery.real_sql, tn, limit=10)

            message += "Query saved successfully"
            return render(request, 'queryform.html', {
                'myquery': myquery,
                'watchlists': watchlists,
                'watchmaps': watchmaps,
                'annotators': annotators,
                'topic': tn,
                'is_owner': True,
                'logged_in': logged_in,
                'email': email,
                'new': False,
                'newandloggedin': False,
                'schemas': schemas,
                'message': message})
        else:
            # New query, blank query form
            message += 'New query'
            return render(request, 'queryform.html', {
                'watchlists': watchlists,
                'watchmaps': watchmaps,
                'annotators': annotators,
                'random': '%d' % random.randrange(1000),
                'email': email,
                'is_owner': False,
                'logged_in': logged_in,
                'email': email,
                'new': True,
                'newandloggedin': logged_in,
                'schemas': schemas,
                'message': message,
            })

    # Existing query
    myquery = get_object_or_404(filter_query, mq_id=mq_id)
    is_owner = logged_in and (request.user == myquery.user)

    if not is_owner and myquery.public == 0:
        return render(request, 'error.html', {'message': 'This query is private'})

    # Existing query, owner wants to change it
    if request.method == 'POST' and logged_in:

        #        s = ''   ####
        #        for k,v in request.POST.items():
        #            s += '%s --> %s<br/>' % (k,v)
        #        return render(request, 'error.html', {'message': s})

        # Delete the given query
        if 'delete' in request.POST:
            myquery.delete()
            delete_stream_file(request, myquery.name)
            return redirect('/explore')

        # Copy the given query
        if 'copy' in request.POST:
            newname = 'Copy_Of_' + myquery.name + '_'
            letters = string.ascii_lowercase
            newname += ''.join(random.choice(letters) for i in range(6))
            tn = topic_name(request.user.id, newname)
            mq = filter_query(user=request.user, name=newname,
                              description=myquery.description,
                              public=0, active=0,
                              selected=myquery.selected,
                              conditions=myquery.conditions, tables=myquery.tables,
                              real_sql=myquery.real_sql, topic_name=tn)
            mq.save()

            # after saving, delete the topic and push some records from the database
            if myquery.active == 2:
                message + topic_refresh(myquery.real_sql, tn, limit=10)

            message += 'Query copied<br/>'
            return redirect('/query/%d/' % mq.mq_id)

        # Update the given query from the post
        else:
            myquery.name = request.POST.get('name')
            myquery.description = request.POST.get('description')
            myquery.selected = request.POST.get('selected')
            myquery.tables = request.POST.get('tables')
            myquery.conditions = request.POST.get('conditions')
            public = request.POST.get('public')
            e = check_query(myquery.selected, myquery.tables, myquery.conditions)
            if e:
                return render(request, 'error.html', {'message': str(e) + '<br/>'})

            myquery.real_sql = build_query(myquery.selected, myquery.tables, myquery.conditions)
            e = check_query_zero_limit(myquery.real_sql)
            if e:
                return render(request, 'error.html', {'message': str(e) + '<br/>'})

            tn = topic_name(request.user.id, myquery.name)
            myquery.topic_name = tn
            try:
                myquery.active = int(request.POST.get('active'))
            except:
                myquery.active = 0

            if public == 'on':
                if myquery.public is None or myquery.public == 0:
                    myquery.public = 1  # if set to 1 or 2 leave it as it is
            else:
                myquery.public = 0
            delete_stream_file(request, myquery.name)

            # after saving, delete the topic and push some records from the database
            if myquery.active == 2:
                message += topic_refresh(myquery.real_sql, tn, limit=10)

            message += 'Query %s updated<br/>' % myquery.name

        myquery.save()
        return render(request, 'queryform.html', {
            'myquery': myquery,
            'watchlists': watchlists,
            'watchmaps': watchmaps,
            'annotators': annotators,
            'topic': tn,
            'is_owner': is_owner,
            'logged_in': logged_in,
            'email': email,
            'new': False,
            'newandloggedin': False,
            'schemas': schemas,
            'message': message})

    # Existing query, view it
    return render(request, 'queryform.html', {
        'myquery': myquery,
        'watchlists': watchlists,
        'watchmaps': watchmaps,
        'annotators': annotators,
        'topic': myquery.topic_name,
        'is_owner': is_owner,
        'logged_in': logged_in,
        'email': email,
        'new': False,
        'newandloggedin': False,
        'schemas': schemas,
        'message': message})
