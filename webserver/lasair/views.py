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
    """
    Get the most recent events siutable for display on front page.
    The events are grouped by class and age into sets that will all be the same 
    colour and size, for example iclass=0 means SN and iage=2 means age between 2 and 5 days.
    Note that age is time since the most recent alert.
    """
    sherlock_classes = ['SN',     'NT',     'CV',     'AGN']
    base_colors =      ['FF0000', 'FF00FF', '1E90FF', 'FFC20A']

    # query finds only mag<17 alerts with at least 2 in light curve, with age < 7
    query = """
       SELECT objects.objectId,
           objects.ramean, objects.decmean,
           objects.gmag, objects.rmag, jdnow()-objects.jdmax AS age,
           sherlock_classifications.classification AS class
       FROM objects, sherlock_classifications
       WHERE objects.objectId=sherlock_classifications.objectId
           AND objects.jdmax > jdnow()-7
           AND (objects.gmag < 17 OR objects.rmag < 17)
           AND objects.ncandgp > 1
           AND sherlock_classifications.classification in
    """
    S = ['"' + sherlock_class + '"' for sherlock_class in sherlock_classes]
    query += '(' + ','.join(S) + ')'

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute (query)

    nclass = len(sherlock_classes)
    nage = 5

    # 2D array of colors by class and age
    colors = [[] for iclass in range(nclass)]
    for iclass in range(nclass):
        for iage in range(nage):
            r = int(int(base_colors[iclass][0:2], 16) * (0.8 ** iage))
            g = int(int(base_colors[iclass][2:4], 16) * (0.8 ** iage))
            b = int(int(base_colors[iclass][4:6], 16) * (0.8 ** iage))
            colors[iclass].append('#%06x' % (256*(256*r + g) + b))

    # 2D array of alerts by class and age
    alerts = [[] for iclass in range(nclass)]
    for iclass in range(nclass):
        alerts[iclass] = [[] for iage in range(nage)]

    for row in cursor:
        if row['gmag']:
            if row['rmag']: mag = min(row['gmag'], row['rmag'])
            else:           mag = row['gmag']
        else:
            if row['rmag']: mag = row['rmag']
            else:           continue

        iclass = sherlock_classes.index(row['class'])

        age = row['age']
        if age < 1:    iage = 0
        elif age < 2:  iage = 1
        elif age < 3:  iage = 2
        elif age < 4:  iage = 3
        else:          iage = 4


        alerts[iclass][iage].append({
            'objectId'   : row['objectId'],
            'age'        : row['age'],
            'class'      : row['class'],
            'mag'        : mag,
            'coordinates': [row['ramean'], row['decmean']]
        })

    message = str(alerts[0][0])[:300]

    try:
        news = open('/home/ubuntu/news.txt').read()
    except:
        news = 'Cannot open news file'

    context = {
        'web_domain': settings.WEB_DOMAIN,
        'alerts'    : str(alerts),
        'colors'    : str(colors),
        'news'      : news,
        'message'   : message
    }
    return render(request, 'index.html', context)
