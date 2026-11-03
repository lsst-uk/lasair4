"""Tests for the synthetic ZTF alert generator."""
import re
import unittest

from seed import paths  # noqa: F401  (PUTS REPO HELPERS ON sys.path)
from seed.alerts import (OBJECT_TYPES, SAMPLE_ALERT_DIR, jd_now, load_sample_alerts,
                         make_alerts, shift_alert_times)
from insert_query import create_insert_query
from seed.seed import DEFAULT_N_OBJECTS, DEFAULT_SEED

OBJECT_ID_PATTERN = re.compile(r'^ZTF\d{2}[a-z]{7}$')
NOW_JD = 2461000.5
FRONT_PAGE_CLASSES = ('SN', 'NT', 'CV', 'AGN')
FRONT_PAGE_MAX_MAG = 17
FRONT_PAGE_MAX_AGE_DAYS = 7
MIN_FRONT_PAGE_OBJECTS = 8


def _is_front_page_object(alert):
    detections = [c for c in [alert['candidate']] + (alert['prv_candidates'] or []) if c.get('candid')]
    latest = {}
    for c in sorted(detections, key=lambda c: c['jd']):
        latest[c['fid']] = c['magpsf']
    nGreen = sum(1 for c in detections if c['fid'] == 1)
    isRecent = max(c['jd'] for c in detections) > NOW_JD - FRONT_PAGE_MAX_AGE_DAYS
    isBright = any(mag < FRONT_PAGE_MAX_MAG for mag in latest.values())
    return (alert['lasair_dev']['sherlock'] in FRONT_PAGE_CLASSES and isRecent and isBright and nGreen > 1)


class MakeAlertsTest(unittest.TestCase):

    def setUp(self):
        self.alerts = make_alerts(seed=42, nObjects=40, nowJd=NOW_JD)

    def test_returns_requested_number_of_alerts_with_unique_ids(self):
        ids = [a['objectId'] for a in self.alerts]
        self.assertEqual(len(ids), 40)
        self.assertEqual(len(set(ids)), 40)

    def test_is_deterministic_for_the_same_seed(self):
        again = make_alerts(seed=42, nObjects=40, nowJd=NOW_JD)
        self.assertEqual([a['objectId'] for a in again], [a['objectId'] for a in self.alerts])
        self.assertEqual(again[0]['candidate']['magpsf'], self.alerts[0]['candidate']['magpsf'])

    def test_object_ids_follow_ztf_format(self):
        for alert in self.alerts:
            self.assertRegex(alert['objectId'], OBJECT_ID_PATTERN)

    def test_every_object_type_is_represented(self):
        types = {a['lasair_dev']['type'] for a in self.alerts}
        self.assertEqual(types, set(OBJECT_TYPES))

    def test_latest_candidate_is_a_detection_no_later_than_now(self):
        for alert in self.alerts:
            cand = alert['candidate']
            self.assertTrue(cand['candid'])
            self.assertLessEqual(cand['jd'], NOW_JD)
            for prv in alert['prv_candidates']:
                self.assertLessEqual(prv['jd'], cand['jd'])

    def test_non_detections_have_no_candid_and_a_limit(self):
        nonDetections = [p for a in self.alerts for p in a['prv_candidates'] if not p.get('candid')]
        self.assertTrue(nonDetections)
        for prv in nonDetections:
            self.assertIn('diffmaglim', prv)
            self.assertIn('field', prv)

    def test_production_feature_code_accepts_every_alert(self):
        for alert in self.alerts:
            result = create_insert_query(alert)
            self.assertIsNotNone(result, alert['objectId'])
            self.assertIn(alert['objectId'], result['query'])

    def test_forced_photometry_has_fields_the_object_page_needs(self):
        needed = {'jd', 'fid', 'forcediffimflux', 'forcediffimfluxunc', 'magzpsci',
                  'procstatus', 'scisigpix', 'sciinpseeing', 'ranr', 'decnr'}
        for alert in self.alerts:
            self.assertTrue(alert['fp_hists'])
            self.assertTrue(needed.issubset(alert['fp_hists'][0]))

    def test_default_seed_gives_objects_for_the_front_page(self):
        # MIRRORS THE QUERY IN webserver/lasair/views.py:index
        alerts = make_alerts(seed=DEFAULT_SEED, nObjects=DEFAULT_N_OBJECTS, nowJd=NOW_JD)
        eligible = [a for a in alerts if _is_front_page_object(a)]
        self.assertGreaterEqual(len(eligible), MIN_FRONT_PAGE_OBJECTS)
        self.assertEqual({a['lasair_dev']['sherlock'] for a in eligible}, set(FRONT_PAGE_CLASSES))

    def test_solar_system_objects_carry_an_ssnamenr(self):
        ssAlerts = [a for a in self.alerts if a['lasair_dev']['type'] == 'SS']
        self.assertTrue(ssAlerts)
        for alert in ssAlerts:
            self.assertNotEqual(alert['candidate']['ssnamenr'], 'null')


class SampleAlertsTest(unittest.TestCase):

    def test_shift_moves_latest_detection_to_target_jd(self):
        alert = {'objectId': 'ZTF20aaaaaaa',
                 'candidate': {'jd': 2459000.5, 'candid': 1},
                 'prv_candidates': [{'jd': 2458990.5, 'candid': None}]}
        shifted = shift_alert_times(alert, targetJd=2461000.5)
        self.assertAlmostEqual(shifted['candidate']['jd'], 2461000.5)
        self.assertAlmostEqual(shifted['prv_candidates'][0]['jd'], 2460990.5)

    def test_shift_does_not_mutate_input(self):
        alert = {'objectId': 'ZTF20aaaaaaa', 'candidate': {'jd': 2459000.5, 'candid': 1},
                 'prv_candidates': None}
        shift_alert_times(alert, targetJd=2461000.5)
        self.assertEqual(alert['candidate']['jd'], 2459000.5)

    def test_loads_repo_sample_alerts_shifted_to_recent(self):
        alerts = load_sample_alerts(SAMPLE_ALERT_DIR, nowJd=NOW_JD)
        self.assertGreaterEqual(len(alerts), 8)
        for alert in alerts:
            self.assertLessEqual(alert['candidate']['jd'], NOW_JD)
            self.assertGreater(alert['candidate']['jd'], NOW_JD - 30)
            self.assertIn('fp_hists', alert)

    def test_jd_now_is_after_2025(self):
        self.assertGreater(jd_now(), 2460676.5)


if __name__ == '__main__':
    unittest.main()
