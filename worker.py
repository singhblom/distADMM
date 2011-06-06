# Task worker
# Connects PULL socket to tcp://localhost:5557
# Collects workloads from ventilator via that socket
# Connects PUSH socket to tcp://localhost:5558
# Sends results to sink via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import time
import sys
import zmq
import numpy as np
from ell1 import *

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.SUB)
receiver.connect("tcp://master:5551")
receiver.setsockopt(zmq.SUBSCRIBE, '')

# Socket to send messages to
sender = context.socket(zmq.PUB)
sender.connect("tcp://master:5558")


# Load and initialize data:
M = np.genfromtxt("m%s.data"%sys.argv[1])
kappa = np.genfromtxt("kappa%s.data"%sys.argv[1])
Z = makeZ(M, rho=1.0)
xk = np.zeros(M.shape[1])
bik = np.zeros(M.shape[0])

# Process tasks forever

while True:
    s = receiver.recv()
    if s == "REPORT":
        sender.send("%s::%s"%(sys.argv[1],' '.join([str(xx) for xx in xk])))
    elif s == "CLEAR":
        xk = np.zeros(M.shape[1])
        bik = np.zeros(M.shape[0])
    else:
        b_rest = np.array([float(ss) for ss in s.strip().split(' ')]) # b_rest = zk - bk - uk
        # Do the work
        b = bik + b_rest
        xk = lasso(M, b, Z, kappa, 1000, rho=1., report=1000)
        bik = dot(M,xk)
        # Send results to sink
        sender.send(' '.join([str(bb) for bb in bik]))
