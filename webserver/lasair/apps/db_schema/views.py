#!/usr/bin/env python
# encoding: utf-8
"""
*tools for working with the Lasair database schema

:Authors:
    Lasair Team
"""
import importlib
from django.shortcuts import render
from .utils import get_schema


def schema_index(request):
    """*render all database schema*

    **Key Arguments:**

    - `request` -- the page request       
    """
    schemas = {
        'objects': get_schema('objects'),
        'sherlock_classifications': get_schema('sherlock_classifications'),
        'crossmatch_tns': get_schema('crossmatch_tns'),
        'annotations': get_schema('annotations'),
    }
    return render(request, 'db_schema/schema_index.html', {'schemas': schemas})
