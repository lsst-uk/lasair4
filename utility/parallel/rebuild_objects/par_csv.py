import os, sys
sys.path.append('..')
from ssh_cluster import run_commands_on_hosts

if len(sys.argv) < 2:
    print('Usage: par_csv.py nhost')
    sys.exit()

print('==============')
os.system('date')
nhost    = int(sys.argv[1])

out         = '/mnt/cephfs/roy/features'
hosts       = [
    '192.168.0.40', 
    '192.168.0.27', 
    '192.168.0.8',
    '192.168.0.25',
    ]

hosts = hosts[:nhost]
print(hosts)

cmdlist = []
for csvfile in os.listdir(out):
    cmd = 'cd /home/ubuntu/lasair4/utility/parallel/rebuild_objects; '
    cmd += 'python3 csv_to_database.py %s'
    cmd = cmd % (out +'/'+ csvfile)
    print (cmd)
    cmdlist.append(cmd)

#run_commands_on_hosts(cmdlist, hosts)

