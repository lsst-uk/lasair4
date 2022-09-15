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
from lasair.db_schema import get_schema, get_schema_dict, get_schema_for_query_selected
from src import db_connect
import re
import sys
sys.path.append('../common')


def index(request):
    context = {
        'web_domain': settings.WEB_DOMAIN
    }
    return render(request, 'index.html', context)


def index2(request):
    """index.

    Args:
        request:
    """
    web_domain = settings.WEB_DOMAIN
    topic = 'lasair_2BrightSNe'

    try:
        jsonstreamdata = open(settings.KAFKA_STREAMS + '/' + topic, 'r').read()
        streamdata = json.loads(jsonstreamdata)
    except:
        return redirect('/')

    objectIds = []
    for s in streamdata['digest']:
        objectId = s['objectId']
        if not objectId in objectIds:
            objectIds.append(objectId)
            if len(objectIds) >= 3:
                break

    datas = []
    json_datas = []
    jdnow = time.time() / 86400 + 2440587.5
    message = ''
    for objectId in objectIds:
        d = obj(objectId)
        fewcand = []
        for c in d['candidates']:
            if 'candid' in c:
                if len(fewcand) > 9 or jdnow - c['jd'] > 30:
                    break
                fewcand.append(c)
                mjdmin_ago = jdnow - c['jd']
        d['candidates'] = fewcand
        d['objectData']['mjdmin_ago'] = mjdmin_ago
        if 'sherlock' in d:
            d['sherlock']['description'] = ''
        if len(fewcand) > 1:
            d['json'] = json.dumps(d)
            datas.append(d)

    return render(request, 'index2.html', {
        'datas': datas, 'message': message,
    })
