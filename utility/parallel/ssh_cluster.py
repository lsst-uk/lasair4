import sys, time, random
from pssh.clients import ParallelSSHClient

def run_commands_on_hosts(cmdlist, hosts):
    clients = [ParallelSSHClient([host]) for host in hosts]
    
    outputs = [None for host in hosts]
    tstart = time.time()
    while 1:
        nfinished = 0
        for i in range(len(clients)):
            if clients[i]:
                # if a job is finished
                if clients[i].finished():
                    # print the outputs
                    if outputs[i]:
                        for host_output in outputs[i]:
                            print("%d: Host %d: exit code %s" % (
                              time.time()-tstart, i, host_output.exit_code))
                            for line in list(host_output.stdout):
                                print('    ' + line)
    
                    # start another if there is a job
                    if len(cmdlist) > 0:
                        cmd = cmdlist.pop()
                        print('%d: Starting %s on host %d' % (
                            time.time()-tstart, cmd, i))
                        outputs[i] = clients[i].run_command(cmd)
                    else:
                        clients[i] = None
            else:
                nfinished += 1
        if nfinished == len(hosts):
            print('All finished in %d seconds' % int(time.time()-tstart))
            break
        else:
            time.sleep(5)
    
if __name__ == "__main__":
# Assumes that each worker can run the program busy.py:
# import sys, math, random, time
# tstart = time.time()
# N = 10000000 * int(sys.argv[1])
# for i in range(N):
#     x = math.sqrt(random.random())
# t = time.time() - t
# print('%d: Finished' % time.time()-tstart)
    nhosts = int(sys.argv[1])

    hosts      = [
    '192.168.0.40',
    '192.168.0.27',
    '192.168.0.8',
    '192.168.0.25',
    ]
    hosts = hosts[:nhosts]
    print(hosts)
    
    cmdlist = []
    for i in range(16):
#        cmd = 'python3 busy.py %s' % random.randrange(2, 7)
        cmd = 'python3 busy.py 100'
        cmdlist.append(cmd)
    
    run_commands_on_hosts(cmdlist, hosts)
