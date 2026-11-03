"""Tests for turning alerts into Cassandra and MySQL rows."""
import copy
import unittest

from seed import paths  # noqa: F401
from seed.alerts import SAMPLE_ALERT_DIR, load_sample_alerts, make_alerts
from seed.cassandra_rows import split_alert
from seed.mysql_rows import SHERLOCK_ATTRIBUTES, make_sherlock, sherlock_query

NOW_JD = 2461000.5


class SplitAlertTest(unittest.TestCase):

    def setUp(self):
        self.alert = make_alerts(seed=1, nObjects=7, nowJd=NOW_JD)[0]

    def test_splits_detections_non_detections_and_forced_photometry(self):
        nPrv = len(self.alert['prv_candidates'])
        nDet = 1 + sum(1 for p in self.alert['prv_candidates'] if p.get('candid'))
        cands, nonCands, forced = split_alert(self.alert)
        self.assertEqual(len(cands), nDet)
        self.assertEqual(len(nonCands), nPrv + 1 - nDet)
        self.assertEqual(len(forced), len(self.alert['fp_hists']))

    def test_rows_use_lowercase_cassandra_column_names(self):
        cands, nonCands, forced = split_alert(self.alert)
        for row in cands + nonCands + forced:
            self.assertEqual(row['objectid'], self.alert['objectId'])
            self.assertTrue(all(k == k.lower() for k in row))

    def test_non_detection_rows_keep_only_ingest_columns(self):
        _, nonCands, _ = split_alert(self.alert)
        expected = {'objectid', 'jd', 'fid', 'diffmaglim', 'nid', 'field',
                    'magzpsci', 'magzpsciunc', 'magzpscirms'}
        for row in nonCands:
            self.assertEqual(set(row), expected)

    def test_detections_get_an_htm16_id(self):
        cands, _, _ = split_alert(self.alert)
        for row in cands:
            self.assertGreater(row['htmid16'], 0)

    def test_does_not_mutate_the_alert(self):
        before = copy.deepcopy(self.alert)
        split_alert(self.alert)
        self.assertEqual(before, self.alert)


class SherlockTest(unittest.TestCase):

    def test_classification_follows_object_type(self):
        alerts = make_alerts(seed=3, nObjects=14, nowJd=NOW_JD)
        for alert in alerts:
            ann = make_sherlock(alert)
            expected = alert['lasair_dev']['sherlock']
            self.assertEqual(ann['classification'], expected)

    def test_query_targets_sherlock_table_with_all_attributes(self):
        alert = make_alerts(seed=3, nObjects=7, nowJd=NOW_JD)[0]
        query = sherlock_query(alert['objectId'], make_sherlock(alert))
        self.assertTrue(query.startswith('REPLACE INTO sherlock_classifications SET'))
        for attr in SHERLOCK_ATTRIBUTES:
            self.assertIn(attr + '=', query)

    def test_every_sample_alert_gets_a_sherlock_classification(self):
        for alert in load_sample_alerts(SAMPLE_ALERT_DIR, nowJd=NOW_JD):
            ann = make_sherlock(alert)
            self.assertEqual(ann['objectId'], alert['objectId'])
            self.assertTrue(ann.get('classification'), alert['objectId'])
            sherlock_query(alert['objectId'], ann)


if __name__ == '__main__':
    unittest.main()
