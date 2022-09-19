

def handle_uploaded_file(f):
    """*handle the upload of a watchlist catalogue*

    **Key Arguments:**

    - `f` -- the upoloaded file

    **Usage:**

    ```python
    cones = handle_uploaded_file(request.FILES['cones_file'])
    ```           
    """
    return f.read().decode('utf-8')


def add_watchlist_metadata(
        watchlists):
    """*add extra metadata to the watchlists and return a list of watchlist dictionaries*

    **Key Arguments:**

    - `watchlists` -- a list of watchlist objects

    **Usage:**

    ```python
    watchlistDicts = add_watchlist_metadata(watchlists)
    ```           
    """
    from lasair.watchlist_catalogue.models import Watchlists, WatchlistCones
    updatedWatchlists = []
    for wlDict, wl in zip(watchlists.values(), watchlists):
        # ADD LIST COUNT
        wlDict['count'] = WatchlistCones.objects.filter(wl_id=wlDict['wl_id']).count()

        # ADD LIST USER
        wlDict['user'] = f"{wl.user.first_name} {wl.user.last_name}"
        wlDict['profile_image'] = wl.user.profile.image.url
        updatedWatchlists.append(wlDict)
    return updatedWatchlists
