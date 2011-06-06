import time
import numpy as np
cimport numpy as np
cimport cython
from numpy import dot,zeros,eye, hstack, concatenate, sqrt
from numpy.linalg import norm,inv

# We now need to fix a datatype for our arrays. I've used the variable
# DTYPE for this, which is assigned to the usual NumPy runtime
# type info object.
DTYPE = np.float64
# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef np.float64_t DTYPE_t

cdef S(np.ndarray t, np.ndarray kappa):
    return (t>kappa)*(t-kappa)+(t<-kappa)*(t+kappa)

@cython.boundscheck(False) # turn of bounds-checking for entire function
def makeZ(np.ndarray[DTYPE_t, ndim=2] M, DTYPE_t rho=1.0):
    """
    Calculates M.T (rho*I + M M.T)^-1 M, which is used in later calculations.
    """
    cdef int numRowsM=M.shape[0]
    cdef np.ndarray[DTYPE_t, ndim=2] Rinv=inv(rho*eye(numRowsM)+dot(M,M.T)) # much smaller
    cdef np.ndarray[DTYPE_t, ndim=2] ret = dot(M.T,dot(Rinv,M))
    return ret


@cython.boundscheck(False) # turn of bounds-checking for entire function
def lasso(np.ndarray[DTYPE_t, ndim=2] M, np.ndarray[DTYPE_t, ndim=1] b, np.ndarray[DTYPE_t, ndim=2] Z, np.ndarray[DTYPE_t, ndim=1] kappa,
          int numberOfIterations, double rho=1., int report=100):
    """
    The lasso is compressed sensing with noise, more or less. It solves
    min_x ||Ax-b||^2_2 + \lambda ||x||_1

    Usage:
    lasso(M, b, Rinv, kappa, iterations, rho, report)
    
    where M is the data matrix, b the measured values, Z a precomputed matrix, kappa the regularization vector, rho the Boyd regularizer, and report an int.
    """
    #Now, define x,y and z, the variables updated in the iteration. We will initialize them to 0:
    cdef int N=M.shape[0]
    cdef int n=M.shape[1]
    cdef np.ndarray[DTYPE_t, ndim=1] x=zeros((n),dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=1] y=zeros((n),dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=1] z=zeros((n),dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=1] zOld=zeros((n),dtype=DTYPE)
    #q is a temporary variable that just saves an intermediate result.
    cdef np.ndarray[DTYPE_t, ndim=1] q=zeros((n),dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=1] q0=dot(M.T,b)
    cdef int cntr
    for cntr in range(numberOfIterations):
        #The Overall x update is
        #x=(M.T*M+rho*eye(size(M,2)))^(-1)*(M.T*b+rho*z-y); %see Steven Boyd et al
        #but it is more efficient to do the following nonobvious way, see Steven
        #Boyd page 21 for matrix inversion lemma
        q=q0+rho*z-y
        x=(1./rho)*(q-dot(Z,q))
        zOld=z
        z=S(x+(1./rho)*y,kappa)
        y=y+rho*(x-z)
        if(cntr%report==0): #ever so often, print out how we are doing
            print "Primal residual size=%.3e\tDual residual size=%.3e"%(norm(x-z),rho*norm(z-zOld))
            print "@iteration=%s out of %s."%(cntr,numberOfIterations)
    return z
