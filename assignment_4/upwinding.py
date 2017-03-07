#Upwinding.py
#Carter Johnson
#MAT228B Assignment 4

#Upwinding method for solving the advection eqn
#on [0,1] with periodic BCs
#u_j^n+1 = (1-v)u_j^n + v u_j-1^n

from __future__ import division
import numpy as np
from numpy import exp, sin, pi
from numpy.linalg import norm
import matplotlib.pyplot as plt
import scipy.sparse as sparse
import scipy.sparse.linalg

def upwinding_matrix(delX, nu):
	#set sparse matrix S for upwinding method
	#u_j^n+1 = (1-v)u_j^n + v u_j-1^n
	#on [0,1] with periodic BCs

	#Set number of grid points
	N = int(round(1/delX))

	#set back-diagonal components
	back_diag = nu*np.ones(N)
	#set diagonal components
	diag = (1-nu)*np.ones(N)
	#set corner component (from periodic domain)
	corner = nu*np.ones(N)

	# Generate the matrix
	A = np.vstack((back_diag, diag, corner))
	S = scipy.sparse.dia_matrix((A,[-1,0, (N-1)]),shape=(N,N))
	return S

def upwinding_method(u0, S, delT, Tf):
	#upwinding method on [0,1] w/ periodic BCs
	#with time step delT up to time Tf
	#using scheme matrix S(delX, nu)

	#start iteration with initial given u0
	u_old = u0+0
	#do Tf/delT time steps
	steps = int(round(Tf/delT))
	# print(steps)
	for t in range(steps):
		#advance u w/ upwinding scheme
		u_next = S.dot(u_old)
		#update u_old
		u_old = u_next+0
		#plot
		# plt.plot(u_next)
		# plt.show()
		# plt.pause(0.05)
		# plt.close()

	return u_next


if __name__ == '__main__':
	#system parameters
	a=1
	Tf = 1
	delX = 0.01
	N = int(round(1/delX))
	delT = 0.9*a*delX
	print(delT)
	nu = a*delT/delX
	#make upwinding method
	S = upwinding_matrix(delX,nu)
	# print(S.toarray())
	#make smooth initial condition
	grid_X = [delX*i for i in range(N)]
	# print(grid_X)
	u0 = np.asarray([sin(2*pi*x) for x in grid_X])
	# print(u0)
	#solve advection eqn using upwinding method up to Tf=1
	u = upwinding_method(u0, S, delT, Tf)
	# print(u)
	print(u0-u)


