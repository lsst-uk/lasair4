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
        return render(request, 'error.html', {'message': 'Cannot open status file for nid=%d' % nid})

    try:
        status = json.loads(jsonstr)
    except:
        status = None
        return render(request, 'error.html', {'message': 'Cannot parse status file for nid=%d' % nid})

    if status and 'today_filter' in status:
        status['today_singleton'] = \
            status['today_filter'] - status['today_filter_out'] - status['today_filter_ss']

    date = date_nid.nid_to_date(nid)
    return render(request, 'status.html', {
        'web_domain': web_domain, 
        'status': status, 
        'date': date, 
        'lasair_grafana_url': settings.LASAIR_GRAFANA_URL,
        'message': message})
