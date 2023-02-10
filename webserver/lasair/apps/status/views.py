import json
from django.shortcuts import render
import src.date_nid as date_nid
import settings


def status_today(request):
    """*return staus report for today*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('status/<int:nid>/', views.status, name='status'),
        ...
    ]
    ```           
    """
    nid = date_nid.nid_now()
    return status(request, nid)


def status(request, nid):
    """*return staus report for a specific night*

    **Key Arguments:**

    - `request` -- the original request
    - `nid` -- the night ID to return status for (days since 2017-01-01)

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('status/<int:nid>/', views.status, name='status'),
        ...
    ]
    ```           
    """
    message = ''
    web_domain = settings.WEB_DOMAIN
    try:
        filename = '%s_%d.json' % (settings.SYSTEM_STATUS, nid)
        jsonstr = open(filename).read()
    except:
        jsonstr = ''
        # return render(request, 'error.html', {'message': 'Cannot open status file for nid=%d' % nid})

    try:
        status = json.loads(jsonstr)
    except:
        status = None
        # return render(request, 'error.html', {'message': 'Cannot parse status file for nid=%d' % nid})

    if status and 'today_filter' in status:
        status['today_singleton'] = \
            status['today_filter'] - status['today_filter_out'] - status['today_filter_ss']

    # KEY: (DEFINITION, COMMENT)
    statusSchema = {
        'today_alert': ('Alerts received by Ingest stage today', ''),
        'today_candidate': ('New detections today', ''),
        'update_time': ('Last Lasair update time (UTC)', ''),
        'today_filter': ('Alerts received by Filter stage today', 'Database Alerts + Solar System Alerts'),
        'today_filter_out': ('Alerts sent to database today', ''),
        'today_filter_ss': ('Solar system detections today', ''),
        'today_ztf': ('Alerts sent by ZTF today', ''),
        'today_database': ('Updated objects in database today', ''),
        'total_count': ("Total objects in database", ''),
        'min_delay': ('Since most recent alert, hours:minutes', ''),
        'nid': ('Night number (nid)', ''),
        'countTNS': ('Number in TNS database', ''),
        'today_singleton': ('Singletons today', '')
    }
    statusOrder = ["total_count", "nid", "update_time", "today_ztf", "today_alert", "today_filter_out", "today_filter_ss", "today_filter", "today_singleton", "today_candidate", "today_database", "min_delay", "countTNS"]

    statusTable = []

    if status:
        statusTable[:] = [(statusSchema[s][0], status[s], statusSchema[s][1]) for s in statusOrder]

    date = date_nid.nid_to_date(nid)
    prettyDate = date_nid.nid_to_pretty_date(nid)
    daysAgo = date_nid.nid_to_days_ago(nid)
    return render(request, 'status.html', {
        'web_domain': web_domain,
        'status': statusTable,
        'date': date,
        'daysAgo': daysAgo,
        'nid': nid,
        'prettyDate': prettyDate,
        'lasair_grafana_url': settings.LASAIR_GRAFANA_URL,
        'message': message})
