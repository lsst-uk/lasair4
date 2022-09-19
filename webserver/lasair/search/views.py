from django.shortcuts import render
from . import conesearch_impl, readcone, distance, sexra, sexde


def conesearch(request):
    """*return conesearch results (search data within request body)*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('conesearch/', views.conesearch, name='conesearch'),
        ...
    ]
    ```           
    """
    if request.method == 'POST':
        cone = request.POST['cone']
        json_checked = False
        if 'json' in request.POST and request.POST['json'] == 'on':
            json_checked = True

        data = conesearch_impl(cone)
        if json_checked:
            return HttpResponse(json.dumps(data, indent=2), content_type="application/json")
        else:
            return render(request, 'search/conesearch.html', {'data': data})
    else:
        return render(request, 'search/conesearch.html', {})
