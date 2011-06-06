import sys
import zmq
import numpy as np
from numpy.linalg import norm

context = zmq.Context()

# Socket to send messages on
sender = context.socket(zmq.PUB)
sender.bind("tcp://*:5551")

# Socket to receive messages on
receiver = context.socket(zmq.SUB)
receiver.bind("tcp://*:5558")
receiver.setsockopt(zmq.SUBSCRIBE, '')

# SET PARAMETERS:

num_iterations = int(sys.argv[1])
rho = 1.0
b = np.genfromtxt("b.data")
num_examples = b.shape[0]
z = np.zeros(num_examples)
zOld = np.zeros(num_examples)
u = np.zeros(num_examples)
Ax = np.zeros(num_examples)

workerIDs = []
for nn,nc in [l.strip().split(':') for l in open('nodelist')]:
    for core in range(1,int(nc)+1):
        workerIDs.append("%s:%s"%(nn,core))
num_workers = len(workerIDs)


for iteration in range(num_iterations):
    # First send tasks for the x-update:
    bik = z-Ax-u
    sender.send(' '.join([str(bb) for bb in bik]))
    Ax = np.zeros(num_examples)
    for task_nbr in range(num_workers):
        s = receiver.recv()
        Ax += np.array([float(ss) for ss in s.strip().split(' ')])
    Ax /= num_workers
    zOld = z
    z = (b+rho*Ax+u)/(rho+num_workers)
    u = u + Ax - z
    print "Primal residual size=%.3e\tDual residual size=%.3e\t@iteration %s"%(norm(Ax-z),rho*norm(z-zOld),iteration)


print "Requesting REPORT ..."
sender.send("REPORT")
x_vals = {}
reports = 0
while reports<num_workers:
    s = receiver.recv()
    try:
        sid, sdata = s.split('::')
        x_vals[sid] = np.array([float(ss) for ss in sdata.strip().split(' ')])
        reports+=1
    except ValueError:
        pass
        
xout = []
for wID in workerIDs:
    xout.extend(x_vals["%s:%s"%(nID,i)])

np.savetxt("testx.data",np.array(xout))
