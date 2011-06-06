import numpy as np

features = 5000
examples = 500
truefeatures = 10

A = np.random.randn(examples,features)
A[:,0] = np.ones(examples)

kappa = np.ones(features)
kappa[0] = 0.

xtrue = np.zeros(features)
xtrue[0] = 10.
for i in range(truefeatures):
    xtrue[np.random.randint(features)]+=5*np.random.randn()

b = np.dot(A,xtrue)+np.random.randn(examples)

workerIDs = []
for nn,nc in [l.strip().split(':') for l in open('nodelist')]:
    for core in range(1,int(nc)+1):
        workerIDs.append("%s:%s"%(nn,core))

last_N = 0
for i,this_N in enumerate(np.linspace(features/workers,features,workers)):
    np.savetxt("m%s.data"%i,A[:,last_N:this_N])
    np.savetxt("kappa%s.data"%i,kappa[last_N:this_N])
    last_N = this_N

np.savetxt("b.data",b)
np.savetxt("truex.data",xtrue)
