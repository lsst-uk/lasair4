import os, sys, time
sys.path.append('../common/src')
import objectStore

dir1 = '/mnt/cephfs/lasair/fits'
dir2 = '/mnt/cephfs/lasair/fits2'
#store1 = objectStore.objectStore(suffix='fits', fileroot=dir1, double=False)
store2 = objectStore.objectStore(suffix='fits', fileroot=dir2, double=True)

# typical filename = '2267526684315015040_cutoutDifference'
n = 0
nfile = 1
start = time.time()
for d4 in sorted(os.listdir(dir1)):
    for filename_fits in os.listdir(dir1 +'/'+ d4):
        filename = filename_fits.split('.')[0]
        n2 = store2.getFileName(filename, mkdir=True)
        cmd = 'cp %s/%s/%s.fits %s' % (dir1, d4, filename, n2)
        os.system(cmd)
        nfile += 1
    t = (time.time() - start)/nfile
    print('Done %s -- %d files at %.0f ms each' % (d4, nfile, 1000*t))
