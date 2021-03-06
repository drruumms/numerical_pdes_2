#Fractional_Step_Reaction_Diffusion.py
#Carter Johnson
#Mat228B Assignment 3

#Fraction Step Strang-splitting method to solve Fitzhugh-Nagumo 
#Reaction-diffusion eqn
#using Peaceman-Rachford ADI scheme on a cell-centered unit square grid
#for solving 2-d homogeneous diffusion part with Neumann BCs
#and runge-kutta 2 for reaction term ode 

from __future__ import division

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from numpy import exp
from numpy.linalg import norm
from tqdm import tqdm
from pylab import savefig
import scipy.sparse as sparse
import scipy.sparse.linalg
from scipy.integrate import ode
from peaceman_rachford import peaceman_rachford_method, peaceman_rachford_step, sparse_matrices

def f(u,a=0.1,I=0,eps=0.005,gamma=2):
	#Reaction terms for Fitzhugh-Negumo model
	return np.c_[(a-u[:,0])*(u[:,0]-1)*u[:,0]-u[:,1]+I, eps*(u[:,0]-gamma*u[:,1])]

def rk2(u,delT):
	#Runge-Kutta 2 Method - simple 2nd order explicit ODE solver
	u_star = u + delT/2*f(u)
	return u+delT*f(u_star)

def strang_split_step(v,w, h, delT, b, L, I):
	#Strang splitting time step for fractional step method solve
	# v = b∆v + R(v,w)
	# w = R(v,w)
	N = int(round(1/h))

	#first solve diffusion on v using ADI scheme for time length ∆t/2
	v_star = peaceman_rachford_step(v,h,delT/2,b,L,I)

	#then solve reaction for ∆t using a ODE solver
	#flatten v and w from grid-lined up matrices into column vectors, put side by side
	v_and_w = np.c_[v_star.flatten(), w.flatten()]
	#solve ODE at each grid point (row of v_and_w) for one time step ∆t
	v_w_star = rk2(v_and_w,delT)
	#reshape back into v, w grid matrices
	v_starstar = np.reshape(v_w_star[:,0], (N,N))
	w_next = np.reshape(v_w_star[:,1], (N,N))

	#solve diffusion on v_starstar for ∆t/2 to get v_next
	v_next = peaceman_rachford_step(v_starstar,h,delT/2,b,L,I)

	return v_next, w_next
	

def frac_step_strang_split(h, delT, Nt, b, v_old, w_old, plotting):
	#Strang splitting fractional step method
	#solve reaction-diffusion eqn for v,w
	#up to time Nt
	N = int(round(1/h))

	#get operators
	[L,I] = sparse_matrices(h)

	#set oldest v,w for ab2 solver
	old_vw = np.c_[v_old.flatten(), w_old.flatten()]

	#set up plotting
	if plotting[0]==1:
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		# `plot_surface` expects `x` and `y` data to be 2D
		grid_X = [h*(i-0.5) for i in range(1,N+1)]
		grid_Y = [h*(j-0.5) for j in range(1, N+1)]
		X, Y = np.meshgrid(grid_X, grid_Y)  
		#keep z limits fixed
		ax.set_zlim(0, 1)
		plt.ion()
		#text
		text = ax.text2D(0.05,0.95, r"$t=0$", transform=ax.transAxes)
		#set colors for plot
		my_col = cm.Reds
		#plot first frame, v(x,y,0)
		frame = ax.plot_surface(X, Y, v_old, cmap=my_col, vmin=-0.25, vmax=1, rstride=4, cstride=4)
		fig.colorbar(frame)
		plt.pause(0.05)
		#save first frame
		if plotting[3]==1:
			frame_no=1
			filename=plotting[2]+'_fig0'+str(frame_no)+'.png'
			savefig(filename)

	#run simulation for Nt time steps
	for t in tqdm(range(Nt+1)):
		#solve for next v and w
		[v_new,w_new] = strang_split_step(v_old,w_old, h, delT, b, L, I)
		
		if plotting[0]==1 and t%plotting[1]==0:
			#plot current v
			ax.collections.remove(frame)
			#make old texts go bye-bye
			for txt in ax.texts:
				txt.set_visible(False)
			text = ax.text2D(0.05,0.95, r"$t=%.3f$" % (t*delT), transform=ax.transAxes)
			frame = ax.plot_surface(X, Y, v_new, cmap=my_col,vmin=-0.25, vmax=1, rstride=4, cstride=4)
			# ax.view_init(30,t/20)
			plt.pause(0.001)
			if plotting[3]==1 and t%(5*plotting[1])==0:
				frame_no=frame_no+1
				if frame_no<10:
					filename=plotting[2]+'_fig0'+str(frame_no)+'.png'
				else:
					filename=plotting[2]+'_fig'+str(frame_no)+'.png'
				savefig(filename)
			# if t==300 or t==600:
			# 	frame_no=frame_no+1
			# 	if frame_no<10:
			# 		filename=plotting[2]+'_fig0'+str(frame_no)+'.png'
			# 	else:
			# 		filename=plotting[2]+'_fig'+str(frame_no)+'.png'
			# 	savefig(filename)


		v_old = v_new + 0
		w_old = w_new


	return v_new, w_new

def part_b_Run(h,delT,plotting):
	#parameters
	N = int(round(1/h))
	Nt = 300*int(round(1/delT))
	a = 0.1
	gamma = 2
	eps = 0.005
	I_current=0
	D = 5*(10**(-5))

	#setup initial data
	grid_X = [h*(i-0.5) for i in range(1,N+1)]
	grid_Y = [h*(j-0.5) for j in range(1, N+1)]
	v0 = np.asarray([[exp(-100*(x**2+y**2)) for x in grid_X] for y in grid_Y])
	w0 = np.asarray([[0*x+0*y for x in grid_X] for y in grid_Y])
	
	#run Fractional Step method to solve up to time Nt
	[v,w] = frac_step_strang_split(h,delT,Nt,D, v0,w0, plotting)

def part_c_Run(h,delT,plotting):
	#parameters
	N = int(round(1/h))
	Nt = 600*int(round(1/delT))
	a = 0.1
	gamma = 2
	eps = 0.005
	I_current=0.0
	D = 5*10**(-5)

	#setup initial data
	grid_X = [h*(i-0.5) for i in range(1,N+1)]
	grid_Y = [h*(j-0.5) for j in range(1, N+1)]
	v0 = np.asarray([[1-2*x for x in grid_X] for y in grid_Y])
	w0 = np.asarray([[0.05*y for x in grid_X] for y in grid_Y])
	
	#run Fractional Step method to solve up to time Nt
	[v,w] = frac_step_strang_split(h,delT,Nt,D, v0,w0, plotting)

if __name__ == '__main__':
	h = 2**(-7)
	delT = 1
	frames=5
	plot_on=1
	gif_on=1
	part_b_Run(h,delT,[plot_on,frames,'partb_fast', gif_on])
	# part_c_Run(h,delT,[plot_on, frames, 'partc_fast', gif_on])	
