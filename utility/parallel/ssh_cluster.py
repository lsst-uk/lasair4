import sys, time, random
from pssh.clients import ParallelSSHClient

def run_commands_on_hosts(cmdlist, hosts):
    tstart = time.time()
    
    clients = [ParallelSSHClient([host]) for host in hosts]
    
    outputs = [None for host in hosts]
        
    while 1:
        nfinished = 0
        for i in range(len(clients)):
            if clients[i]:
                # if a job is finished
                if clients[i].finished():
                    # print the outputs
                    if outputs[i]:
                        for host_output in outputs[i]:
                            stdout = list(host_output.stdout)
                            print("%05d: Host %d: exit code %s, output %s" % (
                              int(time.time()-tstart), i, host_output.exit_code, stdout))
    
                    # start another if there is a job
                    if len(cmdlist) > 0:
                        cmd = cmdlist.pop()
                        print('%05d: Starting %s on host %d' % (
                            int(time.time()-tstart), cmd, i))
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
# N = 10000000 * int(sys.argv[1])
# t = time.time()
# for i in range(N):
#     x = math.sqrt(random.random())
# t = time.time() - t
# print('Finished in %.2f seconds' % t)

    hosts = ['192.168.0.40', '192.168.0.25']
    
    cmdlist = []
    for i in range(7):
        cmd = 'python3 busy.py %s' % random.randrange(10, 40)
        cmdlist.append(cmd)
    
    run_commands_on_hosts(cmdlist, hosts)
