import os, sys
sys.path.append('..')
from ssh_cluster import run_commands_on_hosts

if len(sys.argv) < 3:
    print('Usage: par_runner.py nhost nprocess')
    sys.exit()

print('==============')
os.system('date')
nhost    = int(sys.argv[1])
nprocess = int(sys.argv[2])

global_sjd = 2459260  # 2021-02-14
global_ejd = 2459270  # 2021-02-24
out        = '/mnt/cephfs/roy/features'
hosts      = [
    '192.168.0.27', 
    '192.168.0.8',
    '192.168.0.25',
    '192.168.0.40', 
    ]

hosts = hosts[:nhost]
print(hosts)

cmdlist = []
nchunk     = 20
dt = (global_ejd - global_sjd) / nchunk
for ichunk in range(nchunk):
    sjd = global_sjd + dt*ichunk
    ejd = global_sjd + dt*(ichunk+1)
#    print('Chunk %d: %.2f to %.2f' % (ichunk, sjd, ejd))
    host = hosts[ichunk % len(hosts)]

    cmd = 'cd /home/ubuntu/lasair4/utility/parallel/rebuild_objects; '
    cmd += 'python3 runner.py --sjd=%.2f --ejd=%.2f --out=%s --nprocess=%d'
    cmd = cmd % (sjd, ejd, out, nprocess)
#    print (cmd)
    cmdlist.append(cmd)

run_commands_on_hosts(cmdlist, hosts)

