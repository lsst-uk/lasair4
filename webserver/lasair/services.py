import sys
sys.path.append('../../../common')
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from django.http import JsonResponse
from src.objectStore import objectStore

def fits(request, candid_cutoutType):
    # cutoutType can be cutoutDifference, cutoutTemplate, cutoutScience
    image_store = objectStore(suffix = 'fits', fileroot='/mnt/cephfs/lasair/fits')
    try:
        fitsdata = image_store.getFileObject(candid_cutoutType)
    except:
        fitsdata = ''
    response = HttpResponse(fitsdata, content_type='image/fits')
    response['Content-Disposition'] = 'attachment; filename="%s.fits"' % candid_cutoutType
    return response
