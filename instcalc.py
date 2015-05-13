#!/usr/bin/python

from scipy import optimize
import numpy as np

class GridData(object):
    def __init__(self, data=None):
        if data is None:
            raise Exception("Data must be specified to create a GridData object.")
        self.data = data
        

    def rotationAngle(self):
        """
        input some type of data and calculate the rotation angle based on that data
        @param data - an array of data points or a filename of data representing ....
        @return phi -  rotation angle of grid points wrt astronomical north

        The original Igor program has two functions XFit and YFit.  I believe these are fitting N lsq fits 
        to linear components.  This is how there is a differing X and Y platescale.
        """
        return 

    def plateScale(self, telPos = None, starPos = None):
        """
        calculate the plate scale based on two input observations.
        Change this so that it is not taking x and y data, but generalize
        to accept any x linear coordinates.
        Hmm, lsq fit of only x data will should return plate scale as slope.  Try it.

        Use the previous fitting but return block data as well as human readable data
        """
        print telPos, starPos
        try:
            scale = (telPos[1] - telPos[0])/(starPos[1] - starPos[0])
        except ZeroDivisionError:
            scale = 0
        print scale
        return scale

    def fitData(self, grid = None):
        """
        use numpy lsq fit on the grid of data and return fit equation
        @param grid - A Numpy array of ...

        """
        return 

    def formData(self, f_in = None):
        """
        if data is not in an array then lets make it into an array
        """
        return

class BoresightData(object):
    def __init__(self, data = None):
        if data is None:
            raise Exception("Data must be specified to create a GridData object.")
        self.data = data

    def boresightPos(self):
        """
        input rotational array and return the center position
        """
        center = self.findCenter()
        return

    def calcRadius(self, x,y, xc, yc):
        """ calculate the distance of each 2D points from the center (xc, yc) """
        return np.sqrt((x-xc)**2 + (y-yc)**2)
 
    def f(self, c, x, y):
        """
        calculate the distance between the data points and the center 
        """
        Ri = self.calcRadius(x, y, *c)
        return Ri - Ri.mean()

    def findCenter(self):
        """
        calculate the center of the circle or arc.
        modified from: http://wiki.scipy.org/Cookbook/Least_Squares_Circle
        """
        d = np.transpose(self.data)
        x, y = d[1], d[2]
        center_estimate = np.mean(x), np.mean(y)
        center, ier = optimize.leastsq(self.f, center_estimate, args=(x,y))
        xc, yc = center
        Ri = self.calcRadius(x, y, *center)
        R = Ri.mean()
        res = np.sum((Ri - R)**2)
        print xc, yc, ier
        return xc, yc

    