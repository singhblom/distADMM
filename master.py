import sys
import zmq
import numpy as np

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
u = np.zeros(num_examples)
Ax = np.zeros(num_examples)

for iteration in range(num_iterations):
    # First send tasks for the x-update:
    bik = z-Ax-u
    sender.send(' '.join([str(bb) for bb in bik]))
    Ax = np.zeros(num_examples)
    for task_nbr in range(num_workers):
        s = receiver.recv()
        Ax += np.array([float(ss) for ss in s.strip().split(' ')])
    Ax /= num_workers
    z = (b+rho*Ax+u)/(rho+num_workers)
    u = u + Ax - z
    print "Iteration %s finished."%iteration

print "Requesting REPORT ..."
sender.send("REPORT")
x_vals = {}
for task_nbr in range(num_workers):
    s = receiver.recv()
    sid, sdata = s.split('::')
    x_vals[sid] = np.array([float(ss) for ss in sdata.strip().split(' ')])

xout = []
for node in open("nodelist"):
    nID,nCores = node.strip().split(':')
    for i in range(1,int(nCores)+1): # bash counts inclusive
        xout.extend(x_vals["%s:%s"%(nID,i)])

np.savetxt("testx.data",np.array(xout))
