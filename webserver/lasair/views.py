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
