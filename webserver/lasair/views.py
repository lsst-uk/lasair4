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
    query = """
       SELECT objects.objectId,
           objects.gmag, objects.rmag, jdnow()-objects.jdmax AS age,
           sherlock_classifications.classification AS CLASS
       FROM objects, sherlock_classifications
       WHERE objects.objectId=sherlock_classifications.objectId
           AND objects.jdmax > jdnow()-14
           AND (objects.gmag < 18 OR objects.rmag < 18)
           AND objects.ncandgp > 3
           AND sherlock_classifications.classification in ("AGN", "CV", "NT", "SN")
    """

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute (query)
    alerts = [alert for alert in cursor]
    message = str(alerts)[:300]
    news = open('/home/ubuntu/news.txt').read()
    context = {
        'web_domain': settings.WEB_DOMAIN,
        'alerts'    : alerts,
        'news'      : news,
        'message'   : message
    }
    return render(request, 'index.html', context)
