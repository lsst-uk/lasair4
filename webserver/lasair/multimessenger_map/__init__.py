import dateutil.parser as dp


def jd_from_iso(date):
    """convert and return a Julian Date from ISO format date

     **Key Arguments:**

    - `date` -- date in iso format
    """
    if not date.endswith('Z'):
        date += 'Z'
    parsed_t = dp.parse(date)
    unix = int(parsed_t.strftime('%s'))
    jd = unix / 86400 + 2440587.5
    return jd
