import context
import os, sys, json
import unittest
sys.path.append('../../common/src')
import bad_fits

class CommonBadFitsTest(unittest.TestCase):
    def test_bad_fits(self):
        dir = 'bad_fits_test_files'
        for filename in os.listdir(dir):
            filename = dir +'/'+ filename
            print(filename, bad_fits.bad_moc_file(filename))

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
