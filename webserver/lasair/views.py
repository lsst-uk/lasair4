import importlib
import random
import time
import math
import string
import json
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
import src.date_nid as date_nid

from django.db.models import Q
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import settings
from lasair.apps.db_schema.utils import get_schema, get_schema_dict, get_schema_for_query_selected
from src import db_connect
import re
import sys

sys.path.append('../common')


def index(request):
    context = {
        'web_domain': settings.WEB_DOMAIN
    }
    return render(request, 'index.html', context)


def status_today(request):
    nid  = date_nid.nid_now()
    return status(request, nid)

def status(request, nid):
    message = ''
    web_domain = settings.WEB_DOMAIN
    try:
        filename = '%s_%d.json' % (settings.SYSTEM_STATUS, nid)
        jsonstr = open(filename).read()
    except:
        jsonstr = ''
        return render(request, 'error.html', {'message': 'Cannot open status file for nid=%d'%nid})

    if 1:
#    try:
        status = json.loads(jsonstr)
        return(render(request, 'error.html', {'message': str(status)}))


#    except:
#        status = None
#        return render(request, 'error.html', {'message': 'Cannot parse status file for nid=%d'%nid})

    if status and 'today_filter' in status:
        status['today_singleton'] = \
            status['today_filter'] - status['today_filter_out'] - status['today_filter_ss']

    date = date_nid.nid_to_date(nid)
    return render(request, 'status.html', 
            {'web_domain': web_domain, 'status':status, 'date':date, 'message':message})

