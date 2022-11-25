from lasair.query_builder import check_query, build_query
from src import db_connect
from lasair.apps.db_schema.utils import get_schema, get_schema_dict, get_schema_for_query_selected


def add_filter_query_metadata(
        filter_queries,
        remove_duplicates=False):
    """*add extra metadata to the filter_queries and return a list of filter_queries dictionaries*

    **Key Arguments:**

    - `filter_queries` -- a list of filter_query objects
    - `remove_duplicates` -- remove duplicate filters 

    **Usage:**

    ```python
    filterQueryDicts = add_filter_query_metadata(filter_queries)
    ```           
    """
    # from lasair.watchlist.models import Watchlists, WatchlistCones
    updatedFilterQueryLists = []
    real_sql = []
    for fqDict, fq in zip(filter_queries.values(), filter_queries):
        # ADD LIST COUNT
        # fqDict['count'] = WatchlistCones.objects.filter(wl_id=wlDict['wl_id']).count()

        # ADD LIST USER
        if not remove_duplicates or fq.real_sql not in real_sql:
            fqDict['user'] = f"{fq.user.first_name} {fq.user.last_name}"
            fqDict['profile_image'] = fq.user.profile.image.url
            updatedFilterQueryLists.append(fqDict)
            real_sql.append(fq.real_sql)
        else:
            print("GONE")
    return updatedFilterQueryLists


def run_filter(
        selected,
        tables,
        conditions,
        limit,
        offset,
        mq_id=False,
        query_name=False):
    """run the filter and return the table of results

    **Key Arguments:**

        - `userid` -- the users unique ID
        - `name` -- the name given to the filter

    """
    message = ''
    error = check_query(selected, tables, conditions)
    if error:
        return None, None, None, None, error
    sqlquery_real = build_query(selected, tables, conditions)
    sqlquery_limit = sqlquery_real + ' LIMIT %d OFFSET %d' % (limit, offset)
    message += sqlquery_limit

# lets keep a record of all the queries the people try to execute
#    record_query(request, sqlquery_real)

    nalert = 0
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)

    if query_name:
        topic = topic_name(mq_id, query_name)
    else:
        topic = False

    try:
        cursor.execute(sqlquery_limit)
    except Exception as e:
        error = 'Your query:<br/><b>' + sqlquery_limit + '</b><br/>returned the error<br/><i>' + str(e) + '</i>'
        return None, None, None, None, error

    table = []
    for row in cursor:
        table.append(row)
        nalert += 1

    tableSchema = get_schema_for_query_selected(selected)
    if len(table):
        for k in table[0].keys():
            if k not in tableSchema:
                tableSchema[k] = "custom column"

    return table, tableSchema, nalert, topic, error

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
                       'limit': limit, 'offset': offset,
                       'message': message,
                       "schema": tableSchema})


def topic_name(userid, name):
    """generate a kafka topic name based on userid and query name.

    **Key Arguments:**

        - `userid` -- the users unique ID
        - `name` -- the name given to the filter

    """
    name = ''.join(e for e in name if e.isalnum() or e == '_' or e == '-' or e == '.')
    return 'lasair_' + '%d' % userid + name
