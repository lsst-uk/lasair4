"""Tests for synthetic FITS cutouts."""
import io
import tempfile
import unittest

from astropy.io import fits

from seed import paths  # noqa: F401
from seed.cutouts import CUTOUT_SIZE, CUTOUT_TYPES, make_cutout, write_cutouts
from objectStore import objectStore


class CutoutTest(unittest.TestCase):

    def test_cutout_is_valid_fits_of_expected_size(self):
        blob = make_cutout(seed=5, cutoutType='Science', isDetection=True)
        with fits.open(io.BytesIO(blob)) as hdul:
            self.assertEqual(hdul[0].data.shape, (CUTOUT_SIZE, CUTOUT_SIZE))

    def test_difference_cutout_peaks_at_centre(self):
        blob = make_cutout(seed=5, cutoutType='Difference', isDetection=True)
        with fits.open(io.BytesIO(blob)) as hdul:
            data = hdul[0].data
            centre = CUTOUT_SIZE // 2
            self.assertEqual(data.argmax(), centre * CUTOUT_SIZE + centre)

    def test_written_paths_match_the_webserver_lookup(self):
        with tempfile.TemporaryDirectory() as root:
            store = objectStore(suffix='fits', fileroot=root)
            written = write_cutouts(store, candid=1234567890123456789, imjd=60900, seed=1)
            expected = {store.getFileName('1234567890123456789_cutout%s' % t, 60900)
                        for t in CUTOUT_TYPES}
            self.assertEqual(set(written), expected)


if __name__ == '__main__':
    unittest.main()
