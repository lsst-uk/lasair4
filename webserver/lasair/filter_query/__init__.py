def add_filter_query_metadata(
        filter_queries,
        remove_duplicates=False):
    """*add extra metadata to the filter_queries and return a list of filter_queries dictionaries*

    **Key Arguments:**

    - `filter_queries` -- a list of filter_query objects
    - `remove_duplicates` -- remove duplicate filters 

    **Usage:**

    ```python
    filterQueryDicts = add_filter_query_metadata(filter_queries)
    ```           
    """
    # from lasair.watchlist.models import Watchlists, WatchlistCones
    updatedFilterQueryLists = []
    real_sql = []
    for fqDict, fq in zip(filter_queries.values(), filter_queries):
        # ADD LIST COUNT
        # fqDict['count'] = WatchlistCones.objects.filter(wl_id=wlDict['wl_id']).count()

        # ADD LIST USER
        if not remove_duplicates or fq.real_sql not in real_sql:
            fqDict['user'] = f"{fq.user.first_name} {fq.user.last_name}"
            fqDict['profile_image'] = fq.user.profile.image.url
            updatedFilterQueryLists.append(fqDict)
            real_sql.append(fq.real_sql)
        else:
            print("GONE")
    return updatedFilterQueryLists
