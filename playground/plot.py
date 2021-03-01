from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import numpy as np

def plot_implicit(fn, isovalue, bbox=(-2.5,2.5), elev=0, azim=30):
    """
    create a plot of an implicit function
    fn  ...implicit function (plot where fn==0)
    bbox ..the x,y,and z limits of plotted interval
    """
    xmin, xmax, ymin, ymax, zmin, zmax = bbox*3
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    A = np.linspace(xmin, xmax, 100) # resolution of the contour
    B = np.linspace(xmin, xmax, 15) # number of slices
    A1, A2 = np.meshgrid(A, A) # grid on which the contour is plotted

    # X = A
    # Y = B
    # z = np.copy(A)
    # for i, z in enumerate(B):
    #     z[i] = fn(X,Y,z)

    # ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
    #         cmap='viridis', edgecolor='none')

    for z in B: # plot contours in the XY plane
        X,Y = A1,A2
        Z = fn(X,Y,z) - isovalue
        cset = ax.contour(X, Y, Z+z, [z], zdir='z', colors='red')
        # [z] defines the only level to plot for this contour for this value of z

    for y in B: # plot contours in the XZ plane
        X,Z = A1,A2
        Y = fn(X,y,Z) - isovalue
        cset = ax.contour(X, Y+y, Z, [y], zdir='y', colors='red')

    for x in B: # plot contours in the YZ plane
        Y,Z = A1,A2
        X = fn(x,Y,Z) - isovalue
        cset = ax.contour(X+x, Y, Z, [x], zdir='x', colors='red')
        
## now plot the negative part
    for z in B: # plot contours in the XY plane
        X,Y = A1,A2
        Z = fn(X,Y,z) + isovalue
        cset = ax.contour(X, Y, Z+z, [z], zdir='z', colors='blue')
        # [z] defines the only level to plot for this contour for this value of z

    for y in B: # plot contours in the XZ plane
        X,Z = A1,A2
        Y = fn(X,y,Z) + isovalue
        cset = ax.contour(X, Y+y, Z, [y], zdir='y', colors='blue')

    for x in B: # plot contours in the YZ plane
        Y,Z = A1,A2
        X = fn(x,Y,Z) + isovalue
        cset = ax.contour(X+x, Y, Z, [x], zdir='x', colors='blue')

    # must set plot limits because the contour will likely extend
    # way beyond the displayed level.  Otherwise matplotlib extends the plot limits
    # to encompass all values in the contour.
    ax.set_zlim3d(zmin,zmax)
    ax.set_xlim3d(xmin,xmax)
    ax.set_ylim3d(ymin,ymax)
    ax.view_init(elev, azim)
    plt.show()