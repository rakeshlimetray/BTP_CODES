#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Jonathan Senning <jonathan.senning@gordon.edu>
# Gordon College
# April 22, 1999
# Converted to Python November 2008
#
# $Id$
#
# Use Crank-Nicolson scheme to solve the heat equation in a thin rod.
# The equation solved is
#
#       du     d  du
#       -- = K -- --
#       dt     dx dx
#
# along with boundary conditions
#
#       u(xmin,t) = a(t)
#       u(xmax,t) = b(t)
#
# and initial conditions
#
#       u(x,tmin) = f(x)
#
#-----------------------------------------------------------------------------

import matplotlib
matplotlib.use( 'GTKAgg' )

from pylab import *
import tridiagonal
import time

# Determine the desired plot types.  A value of 1 means show the plot and
# a value of 0 means don't show the plot.

individual_curves = 1           # Show curves during computation
color_image = 0                 # Show pseudocolor plot of solution
contour_plot = 1                # Show contour plot of solution

# Set the value of the thermal diffusivity.

K = 0.25

# Set size of image.  Also, these values are combined with interval sizes to
# compute h (spatial stepsize) and k (temporal stepsize).  Define array
# to hold all time-dependent data.

n = 64                  # Number of spatial intervals
m = 64                  # Number of temporal intervals
u = zeros( ( n+1, m+1 ), float )

# X position of left and right endpoints

xmin, xmax = ( 0, 1 )

# Interval of time: tmin should probably be left at zero

tmin, tmax = ( 0, 2 )

# Generate x and t values.  These aren't really needed to solve the PDE but
# they are useful for computing boundary/initial conditions and graphing.

x = linspace( xmin, xmax, n+1 )
t = linspace( tmin, tmax, m+1 )

# Initial condition f(x)

u[:,0] = 100 * sin( pi * x )

# Boundary conditions: left a(t) and right b(t)

u[0,:] = zeros( m+1, float )                    # Left
u[n,:] = 60 * ( ( 1 - cos( pi * t ) ) / 2.0 )   # Right

# We are using a Crank-Nicolson scheme, and can vary the weighting of the
# u(x,t+k) values with the u(x,t) values using the parameter c (called gamma
# in my notes).
#
# If c == 0 then the iteration reduces to the fully explicit marching scheme
# which is not stable unless k <= (h^2)/2.
#
# If c == 1 then the iteration is fully implicit and is stable for any choice
# of k.
#
# The method should be unconditionally stable if c >= 0.5.  However, when
# c == 0.5 the solution can have undesirable oscillation.

c = 0.75

#-----------------------------------------------------------------------------
#       Should not need to make changes below this point :)
#-----------------------------------------------------------------------------

# Compute step sizes.  Since we also need the square of the spatial step
# size, we go ahead and compute it now as well.

h = ( xmax - xmin ) / float( n )
k = ( tmax - tmin ) / float( m )
h2 = h * h

# Find likely extremes for u

umin, umax = ( u.min(), u.max() )

# Now we are basically done with the setup.  The discritation used leads to
# a tridiagonal linear system.  Here we construct the diagonals of tridiagonal
# matrix.

D = ( 2 * k * K * c + h2 ) * ones( n - 1, float )
A = -k * K * c * ones( n-2, float )
C = -k * K * c * ones( n-2, float )

tridiagonal.factor( A, D, C )

# Plot initial condition curve.  The "sleep()" is used to allow time for the
# plot to appear on the screen before actually starting to solve the problem
# for t > 0.

ion()

if individual_curves != 0:
    plot( x, u[:,0], '-' )
    axis( [xmin, xmax, umin, umax] )
    xlabel( 'x' )
    ylabel( 'Temperature' )
    title( 'step = %3d; t = %f' % ( 0, 0.0 ) )
    draw()
    time.sleep( 2 )

# Main loop.  This consists of computing the appropriate right-hand-side
# vector and then solving the linear system.  We also plot the solution at
# each time step.

for j in xrange( m ):

    B = zeros( n - 1, float )
    B = k * K * ( 1 - c ) * ( u[0:-2,j] + u[2:,j] ) \
                - ( 2 * k * K * ( 1 - c ) - h2 ) * u[1:-1,j]

    B[0]  = B[0]  + k * K * c * u[0,j+1]
    B[-1] = B[-1] + k * K * c * u[n,j+1]

    u[1:-1,j+1] = tridiagonal.solve( A, D, C, B )

    if individual_curves != 0:
        ioff()
        cla()
        plot( x, u[:,j+1], '-' )
        axis( [xmin, xmax, umin, umax] )
        xlabel( 'x' )
        ylabel( 'Temperature' )
        title( 'step = %3d; t = %f' % ( j + 1, ( j + 1 ) * k ) )
        draw()
        draw() # second draw() is necessary to show most recent figure
        ion()

if individual_curves != 0:
    raw_input( "Press Enter to continue... " )

# All done computing solution, now show the desired plots...

if color_image != 0:
    cla()
    imshow( u.transpose() )
    draw()
    raw_input( "Press Enter to continue... " )

if contour_plot != 0:
    umin, umax = ( u.min(), u.max() )
    levels = linspace( umin, umax, 21 )
    cla()
    contour( x, t, u.transpose(), levels )
    xlabel( 'x' )
    ylabel( 't' )
    title( 'Evolution of Temperature in a Thin Rod' )
    draw()
    raw_input( "Press Enter to continue... " )

# End of file
