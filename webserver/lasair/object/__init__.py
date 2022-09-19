from datetime import datetime, timedelta
import time
import json
import math
import ephem
import json
from src import db_connect
from datetime import date
import settings
from lasair.lightcurves import lightcurve_fetcher
from astropy.time import Time


def mjd_now():
    """*return the current UTC time as an MJD*

    **Usage:**

    ```python
    from lasair.object import mjd_now
    mjd = mjd_now()
    ```           
    """
    return time.time() / 86400 + 40587.0


def ecliptic(ra, dec):
    """*return equatorial coordinates as ecliptic coordinates*

    **Usage:**

    ```python
    from lasair.object import ecliptic
    ra, dec = ecliptic(ra, dec)
    ```           
    """
    np = ephem.Equatorial(math.radians(ra), math.radians(dec), epoch='2000')
    e = ephem.Ecliptic(np)
    return (math.degrees(e.lon), math.degrees(e.lat))


def rasex(ra):
    """*return ra in sexigesimal format*

    **Usage:**

    ```python
    from lasair.object import rasex
    ra = rasex(ra)
    ```           
    """
    h = math.floor(ra / 15)
    ra -= h * 15
    m = math.floor(ra * 4)
    ra -= m / 4.0
    s = ra * 240
    return '%02d:%02d:%.3f' % (h, m, s)


def decsex(de):
    """*return dec in sexigesimal format*

    **Usage:**

    ```python
    from lasair.object import decsex
    dec = decsex(dec)
    ```           
    """
    ade = abs(de)
    d = math.floor(ade)
    ade -= d
    m = math.floor(ade * 60)
    ade -= m / 60.0
    s = ade * 3600
    if de > 0.0:
        return '%02d:%02d:%.3f' % (d, m, s)
    else:
        return '-%02d:%02d:%.3f' % (d, m, s)


def objjson(objectId):
    """return all data for an object as a json object (`objectId`,`objectData`,`candidates`,`count_isdiffpos`,`count_all_candidates`,`count_noncandidate`,`sherlock`,`TNS`)

    **Usage:**

    ```python
    from lasair.object import objjson
    objectData = objjson(objID)
    ```  
    """
    objectData = None
    message = ''
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT ncand, ramean, decmean, glonmean, glatmean, jdmin, jdmax '
    query += 'FROM objects WHERE objectId = "%s"' % objectId
    cursor.execute(query)
    for row in cursor:
        objectData = row

    if not objectData:
        return None

    now = mjd_now()
    if objectData:
        if objectData and 'annotation' in objectData and objectData['annotation']:
            objectData['annotation'] = objectData['annotation'].replace('"', '').strip()

        objectData['rasex'] = rasex(objectData['ramean'])
        objectData['decsex'] = decsex(objectData['decmean'])

        (ec_lon, ec_lat) = ecliptic(objectData['ramean'], objectData['decmean'])
        objectData['ec_lon'] = ec_lon
        objectData['ec_lat'] = ec_lat

        objectData['now_mjd'] = '%.2f' % now
        objectData['mjdmin_ago'] = now - (objectData['jdmin'] - 2400000.5)
        objectData['mjdmax_ago'] = now - (objectData['jdmax'] - 2400000.5)

    sherlock = {}
    query = 'SELECT * from sherlock_classifications WHERE objectId = "%s"' % objectId
    cursor.execute(query)
    for row in cursor:
        sherlock = row

    TNS = {}
    query = 'SELECT * '
    query += 'FROM crossmatch_tns JOIN watchlist_hits ON crossmatch_tns.tns_name = watchlist_hits.name '
    query += 'WHERE watchlist_hits.wl_id=%d AND watchlist_hits.objectId="%s"' % (settings.TNS_WATCHLIST_ID, objectId)

    def ordinal_suffix(day):
        if 3 < day < 21 or 23 < day < 31:
            return 'th'
        else:
            return {1: 'st', 2: 'nd', 3: 'rd'}[day % 10]

    cursor.execute(query)
    for row in cursor:
        for k, v in row.items():
            if isinstance(v, datetime):
                suffix = ordinal_suffix(v.day)
                vstr = v.strftime(f"%-d{suffix} %B %Y at %H:%M:%S")
                mjd = Time([v], scale='utc').mjd[0]
                TNS[k] = vstr
                TNS[k + "_mjd"] = mjd
            elif k == "disc_int_name":
                TNS[k] = v.split(",")[0]
            elif v:
                TNS[k] = v

    LF = lightcurve_fetcher(cassandra_hosts=settings.CASSANDRA_HEAD)
    candidates = LF.fetch(objectId)
    LF.close()

    count_isdiffpos = count_all_candidates = count_noncandidate = 0
    for cand in candidates:
        cand['mjd'] = mjd = float(cand['jd']) - 2400000.5
        cand['since_now'] = mjd - now
        if 'candid' in cand:
            count_all_candidates += 1
            candid = cand['candid']
            date = datetime.strptime("1858/11/17", "%Y/%m/%d")
            date += timedelta(mjd)
            cand['utc'] = date.strftime("%Y-%m-%d %H:%M:%S")
            if 'ssnamenr' in cand:
                ssnamenr = cand['ssnamenr']
                if ssnamenr == 'null':
                    ssnamenr = None
            if cand['isdiffpos'] == 'f' or cand['isdiffpos'] == '0':
                count_isdiffpos += 1
        else:
            count_noncandidate += 1
            cand['magpsf'] = cand['diffmaglim']

    if count_all_candidates == 0:
        return None

    if not objectData:
        ra = float(cand['ra'])
        dec = float(cand['dec'])
        objectData = {'ramean': ra, 'decmean': dec,
                      'rasex': rasex(ra), 'decsex': decsex(dec),
                      'ncand': len(candidates), 'MPCname': ssnamenr}
        objectData['annotation'] = 'Unknown object'
        if row['ssdistnr'] > 0 and row['ssdistnr'] < 10:
            objectData['MPCname'] = ssnamenr

    message += 'Got %d candidates and %d noncandidates' % (count_all_candidates, count_noncandidate)

    candidates.sort(key=lambda c: c['mjd'], reverse=True)

    data = {'objectId': objectId,
            'objectData': objectData,
            'candidates': candidates,
            'count_isdiffpos': count_isdiffpos,
            'count_all_candidates': count_all_candidates,
            'count_noncandidate': count_noncandidate,
            'sherlock': sherlock,
            'TNS': TNS, 'message': message,
            }
    return data
