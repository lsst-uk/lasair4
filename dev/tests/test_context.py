"""Tests for watchlist and watchmap hit computation."""
import unittest

from seed import paths  # noqa: F401
from seed.context import AREA_FITS, area_hits, cone_hits


class ConeHitsTest(unittest.TestCase):

    def test_object_inside_radius_is_a_hit_with_separation(self):
        objects = [{'objectId': 'ZTF20aaaaaaa', 'ramean': 10.0, 'decmean': 20.0}]
        cones = [{'cone_id': 7, 'wl_id': 2, 'name': 'c1', 'ra': 10.0, 'decl': 20.0005}]
        hits = cone_hits(objects, cones, radiusArcsec=3.0)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]['cone_id'], 7)
        self.assertAlmostEqual(hits[0]['arcsec'], 1.8, places=1)

    def test_object_outside_radius_is_not_a_hit(self):
        objects = [{'objectId': 'ZTF20aaaaaaa', 'ramean': 10.0, 'decmean': 20.0}]
        cones = [{'cone_id': 7, 'wl_id': 2, 'name': 'c1', 'ra': 10.0, 'decl': 20.01}]
        self.assertEqual(cone_hits(objects, cones, radiusArcsec=3.0), [])


class AreaHitsTest(unittest.TestCase):

    def test_returns_only_objects_inside_the_moc(self):
        # THE SAMPLE MOC COVERS A FEW SQUARE DEGREES AROUND RA 168, DEC -11
        objects = [{'objectId': 'ZTF20aaaaaaa', 'ramean': 169.012, 'decmean': -11.101},
                   {'objectId': 'ZTF20bbbbbbb', 'ramean': 0.0, 'decmean': 89.9}]
        self.assertEqual(area_hits(objects, AREA_FITS), ['ZTF20aaaaaaa'])


if __name__ == '__main__':
    unittest.main()
