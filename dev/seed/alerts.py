"""Build synthetic ZTF alert packets, and load the repo's real sample alerts.

An alert has the same shape as the JSON the Lasair ingest stage publishes:
`objectId`, `candidate` (latest detection), `prv_candidates` (earlier
detections and non-detections) and `fp_hists` (forced photometry). Each
synthetic alert also carries a `lasair_dev` block with its object type and the
Sherlock class it should get, which the rest of the seed code reads.
"""
import copy
import json
import math
import os
import string
import time

import numpy as np

from seed import paths
from seed.models import FAINT_MAG, build_model

SAMPLE_ALERT_DIR = os.path.join(paths.REPO_ROOT, 'tests', 'unit', 'pipeline', 'filter', 'sample_alerts')

OBJECT_TYPES = ('SN', 'NT', 'AGN', 'VS', 'CV', 'BS', 'ORPHAN', 'SS')
SHERLOCK_FOR_TYPE = {'SN': 'SN', 'NT': 'NT', 'AGN': 'AGN', 'VS': 'VS', 'CV': 'CV',
                     'BS': 'BS', 'ORPHAN': 'ORPHAN', 'SS': 'ORPHAN'}
BASELINE_DAYS = {'SN': 60, 'NT': 90, 'AGN': 120, 'VS': 120, 'CV': 60, 'BS': 90, 'ORPHAN': 20, 'SS': 6}

JD_UNIX_EPOCH = 2440587.5
JD_NID_ZERO = 2457754.5          # 2017-01-01, NIGHT ID 0
SECONDS_PER_DAY = 86400.0
CADENCE_DAYS = 2.0
LIMIT_MEAN, LIMIT_SIGMA = 20.5, 0.3
MAGZPSCI = 26.2
DETECTION_SNR = 5.0
WATCHMAP_CENTRE = (168.3, -11.0)  # INSIDE tests/system/sample_area.fits
WATCHMAP_EVERY = 10               # EVERY NTH OBJECT IS PLACED IN THE WATCHMAP AREA
CANDID_BASE = 2_500_000_000_000_000_000
FP_FIELDS = ('field', 'rcid', 'fid', 'pid', 'rfid', 'sciinpseeing', 'scibckgnd', 'scisigpix',
             'magzpsci', 'magzpsciunc', 'magzpscirms', 'clrcoeff', 'clrcounc', 'exptime',
             'adpctdif1', 'adpctdif2', 'diffmaglim', 'programid', 'jd', 'forcediffimflux',
             'forcediffimfluxunc', 'procstatus', 'distnr', 'ranr', 'decnr', 'magnr',
             'sigmagnr', 'chinr', 'sharpnr')


def jd_now():
    """Return the Julian Date now."""
    return time.time() / SECONDS_PER_DAY + JD_UNIX_EPOCH


def nid_for_jd(jd):
    """Return the ZTF night ID (days since 2017-01-01) for a Julian Date."""
    return int(math.floor(jd - JD_NID_ZERO))


def _load_json_alerts(directory):
    alerts = []
    for name in sorted(os.listdir(directory)):
        if name.endswith('.json'):
            with open(os.path.join(directory, name)) as alertFile:
                alerts.append(json.load(alertFile))
    return alerts


def _candidate_template():
    """A real ZTF candidate dict, used so synthetic candidates have every column."""
    sample = _load_json_alerts(SAMPLE_ALERT_DIR)[0]['candidate']
    return {k: v for k, v in sample.items() if k not in ('objectId', 'htmid16')}


def _object_id(rng, firstJd, usedIds):
    year = 2017 + int((firstJd - JD_NID_ZERO) / 365.25)
    while True:
        letters = ''.join(rng.choice(list(string.ascii_lowercase), 7))
        objectId = 'ZTF%02d%s' % (year % 100, letters)
        if objectId not in usedIds:
            usedIds.add(objectId)
            return objectId


def _position(rng, index):
    if index % WATCHMAP_EVERY == 0:
        return WATCHMAP_CENTRE[0] + rng.uniform(-1, 1), WATCHMAP_CENTRE[1] + rng.uniform(-1, 1)
    ra = rng.uniform(0, 360)
    dec = math.degrees(math.asin(rng.uniform(math.sin(math.radians(-30)), 1)))
    return ra, dec


def _epochs(rng, objectType, baseline):
    if objectType == 'SS':
        before = [baseline - d for d in (5.0, 3.0, 1.0)]
        return [(t, 1 + i % 2) for i, t in enumerate(before)] + [(float(baseline), 2)]
    epochs, t = [], 0.0
    while t <= baseline:
        epochs.append((t, 1))
        epochs.append((t + 0.04, 2))
        t += CADENCE_DAYS + rng.uniform(-0.5, 1.5)
    return epochs


def _flux(mag):
    return 0.0 if mag >= FAINT_MAG else 10 ** (-0.4 * mag)


def _host(rng, objectType):
    """Static properties of the nearest catalogued source."""
    stellar = objectType in ('VS', 'CV', 'BS')
    nuclear = objectType in ('NT', 'AGN')
    if stellar:
        return {'sgscore1': rng.uniform(0.95, 1.0), 'distpsnr1': rng.uniform(0.05, 0.4)}
    if nuclear:
        return {'sgscore1': rng.uniform(0.0, 0.2), 'distpsnr1': rng.uniform(0.05, 0.5)}
    if objectType == 'SN':
        return {'sgscore1': rng.uniform(0.0, 0.2), 'distpsnr1': rng.uniform(0.8, 6.0)}
    return {'sgscore1': rng.uniform(0.3, 0.7), 'distpsnr1': rng.uniform(8.0, 25.0)}


def _measure(rng, model, params, refMag, t, fid):
    """Return (diffMag or None, isdiffpos, sigma, limit) for one epoch."""
    limit = rng.normal(LIMIT_MEAN, LIMIT_SIGMA)
    total = model(params, t, fid)
    refFlux = _flux(refMag) if refMag is not None else 0.0
    diff = _flux(total) - refFlux
    if diff == 0.0:
        return None, 't', None, limit
    diffMag = -2.5 * math.log10(abs(diff))
    if diffMag > limit:
        return None, 't', None, limit
    snr = DETECTION_SNR * 10 ** (0.4 * (limit - diffMag))
    sigma = 1.0857 / snr
    return diffMag + rng.normal(0, sigma), ('t' if diff > 0 else 'f'), sigma, limit


def _detection(template, rng, ctx, epoch, measured):
    jd, fid = epoch
    diffMag, isdiffpos, sigma, limit = measured
    cand = dict(template)
    jitter = 0.1 / 3600.0
    cand.update({
        'jd': jd, 'fid': fid, 'nid': nid_for_jd(jd), 'pid': ctx['pidBase'] + ctx['counter'],
        'candid': CANDID_BASE + ctx['index'] * 100_000 + ctx['counter'],
        'ra': ctx['ra'] + rng.normal(0, jitter), 'dec': ctx['dec'] + rng.normal(0, jitter),
        'magpsf': diffMag, 'sigmapsf': sigma, 'isdiffpos': isdiffpos, 'diffmaglim': limit,
        'rb': rng.uniform(0.75, 0.99), 'drb': rng.uniform(0.8, 0.999), 'magzpsci': MAGZPSCI,
        'magnr': ctx['refMag'], 'sigmagnr': 0.02 if ctx['refMag'] else None,
        'distnr': ctx['host']['distpsnr1'] if ctx['refMag'] else -999.0,
        'ssnamenr': ctx['ssnamenr'], 'ssdistnr': 0.4 if ctx['ssnamenr'] != 'null' else -999.0,
        'ssmagnr': diffMag if ctx['ssnamenr'] != 'null' else -999.0,
        'sgscore1': ctx['host']['sgscore1'], 'distpsnr1': ctx['host']['distpsnr1'],
        'sgmag1': (ctx['refMag'] or 21.0) + 0.3, 'srmag1': ctx['refMag'] or 21.0,
        'jdstarthist': ctx['firstJd'], 'jdendhist': jd,
    })
    return cand


def _non_detection(template, ctx, epoch, limit):
    jd, fid = epoch
    return {'jd': jd, 'fid': fid, 'nid': nid_for_jd(jd), 'pid': ctx['pidBase'] + ctx['counter'],
            'candid': None, 'diffmaglim': limit, 'field': template['field'],
            'rcid': template['rcid'], 'programid': 1, 'magzpsci': MAGZPSCI,
            'magzpsciunc': 0.01, 'magzpscirms': 0.03, 'isdiffpos': None, 'magpsf': None,
            'sigmapsf': None, 'ra': None, 'dec': None}


def _forced(rng, ctx, epoch, measured, model, params):
    jd, fid = epoch
    limit = measured[3]
    refFlux = _flux(ctx['refMag']) if ctx['refMag'] is not None else 0.0
    diff = _flux(model(params, jd - ctx['startJd'], fid)) - refFlux
    zeroPointScale = 10 ** (0.4 * MAGZPSCI)
    unc = 10 ** (-0.4 * limit) / DETECTION_SNR * zeroPointScale
    fp = {name: None for name in FP_FIELDS}
    fp.update({'jd': jd, 'fid': fid, 'field': 600, 'rcid': 30, 'pid': ctx['pidBase'] + ctx['counter'],
               'programid': 1, 'magzpsci': MAGZPSCI, 'magzpsciunc': 0.01, 'magzpscirms': 0.03,
               'exptime': 30.0, 'diffmaglim': limit, 'procstatus': '0',
               'scisigpix': rng.uniform(5, 15), 'sciinpseeing': rng.uniform(1.5, 3.0),
               'forcediffimflux': diff * zeroPointScale + rng.normal(0, unc),
               'forcediffimfluxunc': unc, 'ranr': ctx['ra'], 'decnr': ctx['dec']})
    return fp


def _make_one(rng, template, index, objectType, nowJd, usedIds):
    baseline = BASELINE_DAYS[objectType]
    endJd = nowJd - min(rng.exponential(4.0), 25.0)
    startJd = endJd - baseline
    model, params, refMag = build_model(rng, objectType, baseline)
    ra, dec = _position(rng, index)
    ctx = {'index': index, 'ra': ra, 'dec': dec, 'refMag': refMag, 'startJd': startJd,
           'host': _host(rng, objectType), 'pidBase': 3_000_000_000 + index * 1000,
           'ssnamenr': '%d' % rng.integers(1000, 600000) if objectType == 'SS' else 'null',
           'counter': 0, 'firstJd': None}

    epochs = [(startJd + t, fid) for t, fid in _epochs(rng, objectType, baseline)]
    measurements = [_measure(rng, model, params, refMag, jd - startJd, fid) for jd, fid in epochs]
    detected = [i for i, m in enumerate(measurements) if m[0] is not None]
    if not detected:
        # FORCE THE BRIGHTEST EPOCH TO BE A DETECTION SO EVERY OBJECT HAS ONE
        brightest = min(range(len(epochs)), key=lambda i: model(params, epochs[i][0] - startJd, epochs[i][1]))
        mag = min(model(params, epochs[brightest][0] - startJd, epochs[brightest][1]), 20.0)
        measurements[brightest] = (mag, 't', 0.1, mag + 0.5)
        detected = [brightest]
    lastDetection = detected[-1]
    ctx['firstJd'] = epochs[detected[0]][0]

    history, fpHists = [], []
    for i in range(lastDetection + 1):
        ctx['counter'] = i
        measured = measurements[i]
        if measured[0] is None:
            history.append(_non_detection(template, ctx, epochs[i], measured[3]))
        else:
            history.append(_detection(template, rng, ctx, epochs[i], measured))
        fpHists.append(_forced(rng, ctx, epochs[i], measured, model, params))

    objectId = _object_id(rng, ctx['firstJd'], usedIds)
    candidate = history[-1]
    return {
        'schemavsn': '4.02', 'publisher': 'Lasair dev seed', 'objectId': objectId,
        'candid': candidate['candid'], 'candidate': candidate, 'prv_candidates': history[:-1],
        'fp_hists': fpHists,
        'lasair_dev': {'type': objectType, 'sherlock': SHERLOCK_FOR_TYPE[objectType],
                       'refMag': refMag, 'host': ctx['host']},
    }


def make_alerts(seed, nObjects, nowJd):
    """Return `nObjects` synthetic alerts. The same seed gives the same alerts."""
    rng = np.random.default_rng(seed)
    template = _candidate_template()
    usedIds = set()
    return [_make_one(rng, template, i, OBJECT_TYPES[i % len(OBJECT_TYPES)], nowJd, usedIds)
            for i in range(nObjects)]


def shift_alert_times(alert, targetJd):
    """Return a copy of `alert` moved in time so its latest detection is at `targetJd`."""
    shifted = copy.deepcopy(alert)
    delta = targetJd - shifted['candidate']['jd']
    entries = [shifted['candidate']] + (shifted.get('prv_candidates') or []) + (shifted.get('fp_hists') or [])
    for entry in entries:
        for key in ('jd', 'jdstarthist', 'jdendhist'):
            if entry.get(key):
                entry[key] += delta
        if entry.get('nid') is not None and entry.get('jd'):
            entry['nid'] = nid_for_jd(entry['jd'])
    return shifted


def load_sample_alerts(directory, nowJd):
    """Load the repo's real sample alerts, one per object, moved to the last few weeks."""
    byObject = {}
    for alert in _load_json_alerts(directory):
        best = byObject.get(alert['objectId'])
        if best is None or len(alert.get('prv_candidates') or []) > len(best.get('prv_candidates') or []):
            byObject[alert['objectId']] = alert
    alerts = []
    for i, objectId in enumerate(sorted(byObject)):
        shifted = shift_alert_times(byObject[objectId], targetJd=nowJd - 1.5 * i)
        shifted.setdefault('fp_hists', [])
        alerts.append(shifted)
    return alerts
