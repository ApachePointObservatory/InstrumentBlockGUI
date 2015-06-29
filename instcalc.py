#!/usr/bin/python

from scipy import optimize
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from operator import itemgetter

class GridData(object):
    def __init__(self, data=None, bin = None):
        if data is None:
            raise Exception("Data must be specified to create a GridData object.")
        self.data = data
        self.bin = bin
        

    def rotationAngle(self):
        """
        input some type of data and calculate the rotation angle based on that data
        @param data - an array of data points or a filename of data representing ....
        @return phi -  rotation angle of grid points wrt astronomical north
        The original Igor program has two functions XFit and YFit.  I believe these are fitting N lsq fits 
        to linear components.  This is how there is a differing X and Y platescale.
        """
        d = np.transpose(self.data)
        #print d[0],d[1],d[2],d[3]
        #print
        y_pos = np.unique(d[0])
        x_pos = np.unique(d[1])
        #sort the data
        y_arr = [[],[],[],[]]
        x_arr = [[],[],[],[]]

        for i,y in enumerate(x_pos):
            for n,m in enumerate(d[1]):
                if y == m:
                    x_arr[i].append([d[0][n],d[1][n],d[2][n],d[3][n]])
        for i,y in enumerate(y_pos):
            for n,m in enumerate(d[0]):
                if y == m:
                    #print i,n,y,m
                    #print [d[0][n],d[1][n],d[2][n],d[3][n]]
                    y_arr[i].append([d[0][n],d[1][n],d[2][n],d[3][n]])

        ymAng=[]
        ymPlate=[]
        xmAng=[]
        xmPlate=[]

        for index,cat in enumerate(range(len(y_arr)-1)):
            fit = np.transpose(y_arr[index])
            #print fit
            #fit the ccd x,y pos for the same x boresight
            m_rot = self.fitData(fit[2],fit[3])
            ymAng.append(self.rotAng(m_rot))

            #call in the x telescope and x ccd data to determine plate scale
            m_scale= self.fitData(fit[1],fit[3])
            ymPlate.append(self.plateScale(m_scale, self.bin))

        for index,cat in enumerate(range(len(x_arr)-1)):
            fit = np.transpose(x_arr[index])
            #print fit
            #fit the ccd x,y pos for the same x boresight
            m_rot = self.fitData(fit[3],fit[2])
            xmAng.append(self.rotAng(m_rot))

            #call in the x telescope and x ccd data to determine plate scale
            m_scale= self.fitData(fit[0],fit[2])
            xmPlate.append(self.plateScale(m_scale, self.bin))

        comb_coords = []

        for i in range(len(self.data[2])):
            comb_coords.append([self.data[2][i],self.data[3][i]])

        arranged = sorted(comb_coords,key=itemgetter(0))

        line1 = arranged[0:3]
        line2 = arranged[3:6]
        line3 = arranged[6:9]
        line_list = np.array([line1,line2,line3])
        slope_list = []
        yint_list = []

        for item in line_list:
            print item
            print item.T
            slope, yint = self.fitData(item.T[0],item.T[1])
            slope_list.append(slope)
            yint_list.append(yint)
 
        print slope_list
        print yint_list
        
        #print xmAng, xmPlate
        #print ymAng, ymPlate

        return slope_list, yint_list

    def plateScale(self, m = None, bin = None):
        """
        calculate the plate scale based on two input observations.
        Change this so that it is not taking x and y data, but generalize
        to accept any x linear coordinates.
        Hmm, lsq fit of only x data will should return plate scale as slope.  Try it.
        Use the previous fitting but return block data as well as human readable data
        """
        scale = m * bin
        #print 'plate scale: ' +str(m) + ' pix/deg (binned)'
        #print 'plate scale: ' +str(scale) + ' pix/deg (unbinned)'
        #print 'scale: ' +str(1/(m/3600.)) + ' arcsec/pix (binned)'
        #print 'scale: ' +str(1/(scale/3600.)) + ' arcsec/pix (unbinned)'
        return scale

    def rotAng(self, m = None):
        x = 100
        y = (m*x)
        phi = self.convert(y,x)
        theta = ((phi*180.)/np.pi)
        #print 'rotation: ' +str(theta)
        return theta

    def fitData(self, x_arr = None, y_arr = None):
        """
        use numpy lsq fit on the grid of data and return fit equation
        @param grid - A Numpy array of ...
        """
        #print x_arr, y_arr
        A = np.vstack([x_arr, np.ones(len(x_arr))]).T
        #print A
        m,c = np.linalg.lstsq(A,y_arr)[0]
        return m,c

    def convert(self, x = None, y = None):
        phi = np.arctan2(x, y)
        return phi

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
        circleInfo = self.findCenter()
        #self.graphRing(circleInfo,canvas,fig)
        return circleInfo

    def calcRadius(self, x,y, xc, yc):
        """ calculate the distance of each 2D points from the center (xc, yc) """
        radius =  np.sqrt((x-xc)**2 + (y-yc)**2)
        return radius
 
    def f(self, c, x, y):
        """
        calculate the distance between the data points and the center 
        """
        R_i = self.calcRadius(x, y, *c)
        return R_i - R_i.mean()

    def findCenter(self):
        """
        calculate the center of the circle or arc.
        modified from: http://wiki.scipy.org/Cookbook/Least_Squares_Circle
        """
        
        x, y = self.data[0], self.data[1]
        center_estimate = np.mean(x), np.mean(y)
        center, ier = optimize.leastsq(self.f, center_estimate, args=(x,y))
        xc, yc = center
        R_i = self.calcRadius(x, y, *center)
        R = R_i.mean()
        res = np.sum((R_i - R)**2)
        return xc, yc, R
