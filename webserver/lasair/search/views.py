from django.shortcuts import render
from . import conesearch_impl, readcone, distance, sexra, sexde
import re
from src import db_connect


def search(request):
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
        query = request.POST['query']
        results = do_search(query)
        print(results)
        json_checked = False
        if 'json' in request.POST and request.POST['json'] == 'on':
            json_checked = True

        # data = conesearch_impl(query)
        if json_checked:
            return HttpResponse(json.dumps(results, indent=2), content_type="application/json")
        else:
            return render(request, 'search/search.html', {'results': results})
    else:
        return render(request, 'search/search.html', {})


def do_search(
    query
):
    """*determine the type of search the user is requesting*

    **Key Arguments:**

    - `query` -- the text query entered in to the search box

    **Usage:**

    ```python
    usage code 
    ```           
    """

    objectColumns = 'o.objectId, o.ramean,o.decmean, o.rmag, o.gmag, jdnow()-o.jdmax as "last detected (days ago)"'

    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)

    objectName = re.compile(r'^\w\S*', re.S)
    objectMatch = objectName.match(query)

    if objectMatch:
        objectName = objectMatch.group()

        query = f"select {objectColumns} from objects o where o.objectId = '{objectName}'"

        cursor.execute(query)
        results = cursor.fetchall()

    return results

# use the tab-trigger below for new function
# xt-def-simple-function-template
