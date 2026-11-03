"""Build MySQL rows for objects and Sherlock classifications.

Both queries come from the production feature code in
`pipeline/filter/features_ZTF/insert_query.py`, so the `objects` columns are
computed exactly as the filter stage computes them.
"""
import math
import zlib

from seed import paths  # noqa: F401
from insert_query import create_insert_annotation, create_insert_query

# SAME LIST AS tests/unit/pipeline/filter/make_features_test.py
SHERLOCK_ATTRIBUTES = [
    'classification', 'objectId', 'association_type', 'catalogue_table_name',
    'catalogue_object_id', 'catalogue_object_type', 'raDeg', 'decDeg',
    'separationArcsec', 'northSeparationArcsec', 'eastSeparationArcsec',
    'physical_separation_kpc', 'direct_distance', 'distance', 'z', 'photoZ',
    'photoZErr', 'Mag', 'MagFilter', 'MagErr', 'classificationReliability',
    'major_axis_arcsec', 'annotator', 'additional_output', 'description', 'summary',
]

_CATALOGUES = {
    'SN': ('NED_D', 'galaxy', 'synonym'),
    'NT': ('SDSS/2MASS', 'galaxy', 'synonym'),
    'AGN': ('MILLIQUAS', 'agn', 'synonym'),
    'VS': ('GAIA_DR2', 'star', 'synonym'),
    'CV': ('RITTER_CV', 'cv', 'synonym'),
    'BS': ('GSC/GAIA', 'star', 'synonym'),
}
_DESCRIPTIONS = {
    'SN': 'The transient is possibly associated with a galaxy; a supernova candidate.',
    'NT': 'The transient is synonymous with the core of a galaxy; a nuclear transient candidate.',
    'AGN': 'The transient is synonymous with a known AGN.',
    'VS': 'The transient is synonymous with a catalogued star; a variable star candidate.',
    'CV': 'The transient is synonymous with a known cataclysmic variable.',
    'BS': 'The transient is close to a bright star; likely an artefact.',
    'ORPHAN': 'The transient is not obviously associated with any catalogued source.',
}
ARCSEC_PER_DEG = 3600.0
KPC_PER_ARCSEC_PER_Z = 4.8 * 1000 / 3.0e5 * 206.265  # LOW-Z APPROXIMATION


def object_query(alert):
    """Return the `REPLACE INTO objects` query for an alert, or None."""
    result = create_insert_query(alert)
    return result['query'] if result else None


def _host_fields(alert, classification):
    meta = alert['lasair_dev']
    cand = alert['candidate']
    separation = meta['host']['distpsnr1']
    angle = (zlib.crc32(alert["objectId"].encode()) % 360) * math.pi / 180
    north, east = separation * math.cos(angle), separation * math.sin(angle)
    table, objectType, association = _CATALOGUES[classification]
    fields = {
        'association_type': association, 'catalogue_table_name': table,
        'catalogue_object_type': objectType,
        'catalogue_object_id': 'DEV J%08.4f%+08.4f' % (cand['ra'], cand['dec']),
        'raDeg': cand['ra'] - east / ARCSEC_PER_DEG / max(math.cos(math.radians(cand['dec'])), 1e-6),
        'decDeg': cand['dec'] - north / ARCSEC_PER_DEG,
        'separationArcsec': round(separation, 3), 'northSeparationArcsec': round(north, 3),
        'eastSeparationArcsec': round(east, 3), 'Mag': meta['refMag'] or 19.5, 'MagFilter': 'r',
        'MagErr': 0.05, 'classificationReliability': 1, 'major_axis_arcsec': 4.0,
    }
    if classification in ('SN', 'NT', 'AGN'):
        z = 0.02 + (zlib.crc32(alert["objectId"].encode()) % 1000) / 10000.0
        fields.update({'z': round(z, 4), 'distance': round(z * 4280, 1),
                       'physical_separation_kpc': round(separation * z * KPC_PER_ARCSEC_PER_Z, 2)})
    return fields


FALLBACK_CLASSIFICATION = 'ORPHAN'


def make_sherlock(alert):
    """Return a Sherlock annotation dict for an alert."""
    for ann in (alert.get('annotations') or {}).get('sherlock', []):
        if 'classification' not in ann:
            continue
        ann = dict(ann)
        ann.pop('transient_object_id', None)
        ann['objectId'] = alert['objectId']
        return ann
    # REAL SAMPLE ALERTS WITHOUT A USABLE SHERLOCK ANNOTATION ARE TREATED AS ORPHANS
    classification = alert.get('lasair_dev', {}).get('sherlock', FALLBACK_CLASSIFICATION)
    ann = {'objectId': alert['objectId'], 'classification': classification,
           'annotator': 'Lasair dev seed', 'additional_output': 'synthetic',
           'description': _DESCRIPTIONS[classification],
           'summary': '%s (synthetic)' % classification}
    if classification != 'ORPHAN':
        ann.update(_host_fields(alert, classification))
    return ann


def sherlock_query(objectId, ann):
    """Return the `REPLACE INTO sherlock_classifications` query for one annotation."""
    return create_insert_annotation(objectId, 'sherlock', ann, SHERLOCK_ATTRIBUTES,
                                    'sherlock_classifications', replace=True)
