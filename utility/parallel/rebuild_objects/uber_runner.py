import os, sys
s = 0
e = 2459260
n = 3
esn = (e-s) // n
print(esn)
directory = 'csvfiles/out'
hosts = ['192.168.0.40']

for i in range(n):
    sta = s + esn*i
    if i == n-1:
        end = e
    else:
        end = s + esn*(i+1)
    print(sta, end)
    host = hosts[i % len(hosts)]

    cmd = 'ssh -n -f %s '
    cmd += '"sh -c \'cd /home/ubuntu/lasair4/utility/dask/rebuild_objects; '
    cmd += 'nohup python3 runner.py %d %d %s > /dev/null 2>&1 &\'"'
    cmd = cmd % (host, sta, end, directory)

    print (cmd)
    os.system(cmd)


