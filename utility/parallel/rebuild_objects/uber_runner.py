import os, sys
global_sjd = 0
global_ejd = 2459260
nchunk     = 3
nprocess   = 2
out        = 'csvfiles'
hosts      = ['192.168.0.40']

dt = (global_ejd - global_sjd) / nchunk
for ichunk in range(nchunk):
    sjd = global_sjd + dt*ichunk
    ejd = global_sjd + dt*(ichunk+1)
    print('Chunk %d: %.2f to %.2f' % (ichunk, sjd, ejd))
    host = hosts[ichunk % len(hosts)]

    cmd = 'ssh -n -f %s '
    cmd += '"sh -c \'cd /home/ubuntu/lasair4/utility/parallel/rebuild_objects; '
    cmd += 'nohup python3 runner.py --sjd=%.2f --ejd=%.2f --out=%s --nprocess=%d'
    cmd += ' &\'"'
    cmd = cmd % (host, sjd, ejd, out, nprocess)

    print (cmd)
    os.system(cmd)


