#!/usr/bin/python

from scipy import optimize
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from operator import itemgetter

class GridData(object):
    def __init__(self, data, bin = 2):
        if data is None:
            raise Exception("Data must be specified to create a GridData object.")
        self.data = data
        self.bin = bin
        

    def rotationAngle(self,canvas,fig):
        """
        input some type of data and calculate the rotation angle based on that data
        @param data - an array of data points or a filename of data representing ....
        @return phi -  rotation angle of grid points wrt astronomical north

        The original Igor program has two functions XFit and YFit.  I believe these are fitting N lsq fits 
        to linear components.  This is how there is a differing X and Y platescale.
        """
        comb_coords = []
        for i in range(len(self.data[0])):
            comb_coords.append((self.data[0][i],self.data[1][i]))
        arranged = sorted(comb_coords,key=itemgetter(0))
        if len(self.data[0]) == 9:
            line1 = arranged[0:3]
            line2 = arranged[3:6]
            line3 = arranged[6:9]
            line_list = [line1,line2,line3]
        slope_list = []
        yint_list = []
        for item in line_list:
            slope, yint = self.fitData(item)
            slope_list.append(slope)
            yint_list.append(yint)

        rotang_list = []
        for i in range(len(slope_list)):
            rotang_list.append(self.rotAng(slope_list[i]))
        #d = np.transpose(self.data)
        #print d[0],d[1],d[2],d[3]
        #print
        """y_pos = np.unique(self.data[0])
        x_pos = np.unique(self.data[1])
        #sort the data
        y_arr = [[],[],[],[]]
        x_arr = [[],[],[],[]]

        for i,y in enumerate(x_pos):
            for n,m in enumerate(self.data[1]):
                if y == m:
                    x_arr[i].append([self.data[0][n],self.data[1][n],self.data[2][n],self.data[3][n]])
        for i,y in enumerate(y_pos):
            for n,m in enumerate(self.data[0]):
                if y == m:
                    #print i,n,y,m
                    #print [d[0][n],d[1][n],d[2][n],d[3][n]]
                    y_arr[i].append([self.data[0][n],self.data[1][n],self.data[2][n],self.data[3][n]])

        ymAng=[]
        ymPlate=[]
        xmAng=[]
        xmPlate=[]
        for index,cat in enumerate(range(len(y_arr)-1)):
            fit = np.transpose(y_arr[index])
            print fit
            #fit the ccd x,y pos for the same x boresight
            m_rot = self.fitData(fit[2],fit[3])
            ymAng.append(self.rotAng(m_rot))

            #call in the x telescope and x ccd data to determine plate scale
            m_scale= self.fitData(fit[1],fit[3])
            ymPlate.append(self.plateScale(m_scale, self.bin))

        for index,cat in enumerate(range(len(x_arr)-1)):
            fit = np.transpose(x_arr[index])
            print fit
            #fit the ccd x,y pos for the same x boresight
            m_rot = self.fitData(fit[3],fit[2])
            xmAng.append(self.rotAng(m_rot))

            #call in the x telescope and x ccd data to determine plate scale
            m_scale= self.fitData(fit[0],fit[2])
            xmPlate.append(self.plateScale(m_scale, self.bin))

        print xmAng, xmPlate
        print ymAng, ymPlate"""
        self.graphGrid(canvas,fig,slope_list,yint_list,rotang_list)
        return 

    def plateScale(self, m, bin):
        """
        calculate the plate scale based on two input observations.
        Change this so that it is not taking x and y data, but generalize
        to accept any x linear coordinates.
        Hmm, lsq fit of only x data will should return plate scale as slope.  Try it.

        Use the previous fitting but return block data as well as human readable data
        """
        scale = m * bin
        print 'plate scale: ' +str(m) + ' pix/deg (binned)'
        print 'plate scale: ' +str(scale) + ' pix/deg (unbinned)'
        print 'scale: ' +str(1/(m/3600.)) + ' arcsec/pix (binned)'
        print 'scale: ' +str(1/(scale/3600.)) + ' arcsec/pix (unbinned)'
        return scale

    def rotAng(self, m):
        x = 100
        y = (m*x)
        phi = self.convert(y,x)
        theta = ((phi*180.)/np.pi)
        print 'rotation: ' +str(theta)
        return theta

    def fitData(self, comb_coords):
        """
        use numpy lsq fit on the grid of data and return fit equation
        @param grid - A Numpy array of ...
        """
        x_arr = [comb_coords[0][0],comb_coords[1][0],comb_coords[2][0]]
        y_arr = [comb_coords[0][1],comb_coords[1][1],comb_coords[2][1]]
        A = np.vstack([x_arr, np.ones(len(x_arr))]).T
        m,c = np.linalg.lstsq(A,y_arr)[0]
        return m, c

    def convert(self, x = None, y = None):
        phi = np.arctan2(x, y)
        return phi

    def formData(self, f_in = None):
        """
        if data is not in an array then lets make it into an array
        """
        return

    def graphGrid(self,canvas,fig,slope_list,yint_list,rotang_list):
        self.ax1 = fig.add_subplot(211)
        self.ax1.clear()

        #plots the intial grid data
        self.ax1.set_title('Grid')
        self.ax1.set_ylabel('y')
        self.ax1.set_xlabel('x')
        self.ax1.plot(self.data[0],self.data[1],'o',clip_on=False,ms=2)

        #plots the fit of each grid line
        for i in range(len(slope_list)):
            y = range(int(min(self.data[1])),int(max(self.data[1])))
            x = []
            for j in range(len(y)):
                x.append((y[j]-yint_list[i])/slope_list[i])
            self.ax1.plot(x,y)
            self.ax1.annotate('rotAng = %.2f'%(rotang_list[i]),(min(x),min(y)),fontsize=8)
        self.ax1.set_aspect('equal',adjustable='box')
        canvas.draw()
        return

class BoresightData(object):
    def __init__(self, data = object):
        if data is None:
            raise Exception("Data must be specified to create a GridData object.")
        self.data = data

    def boresightPos(self,canvas,fig):
        """
        input rotational array and return the center position
        """
        
        circleInfo = self.findCenter()
        self.graphRing(circleInfo,canvas,fig)
        return

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

    #graphs the data points taken from the file, plots the centerpoint and circle estimate, calls to nearCircle to 
    #calculate and display the offset
    def graphRing(self,circleInfo,canvas,fig):
        self.ax1 = fig.add_subplot(212)
        self.ax1.clear()
        self.ax1.set_title('Ring')
        self.ax1.set_ylabel('y')
        self.ax1.set_xlabel('x')
        self.ax1.plot(self.data[0],self.data[1],'o',clip_on=False,ms=2)
        self.ax1.plot(circleInfo[0],circleInfo[1],'ro')
        circle = plt.Circle((circleInfo[0],circleInfo[1]),circleInfo[2],color='r',fill=False)
        self.ax1.add_artist(circle)
        self.ax1.set_aspect('equal',adjustable='box')
        for i in range(len(self.data[0])):
            offset = self.nearCircle(self.data[0][i],self.data[1][i],circleInfo[0],circleInfo[1],circleInfo[2],self.ax1)
            self.ax1.annotate('(%.2f,%.2f)'%(offset[0],offset[1]),(self.data[0][i]+5,self.data[1][i]+5),fontsize=8)
        canvas.draw()
        return

    #defines the line y = mx+b connecting the given data point (x,y) and the circle's centerpoint (xc,yc) then
    #defines circle using centerpoint and radius, finds intersections of the circle and the line
    #and selects the nearest one, with A, B, and C being the points in the quadratic equation of 
    def nearCircle(self,x,y,xc,yc,R,ax1):
        #finding the zeros of the x values
        m = (y-yc)/(x-xc)
        b = y-m*x
        Ax = 1+m**2
        Bx = 2*(-xc+m*(b-yc))
        Cx = xc**2+b**2+yc**2-2*b*yc-R**2
        coeffx = [Ax,Bx,Cx]
        solsx = np.roots(coeffx)
        closex = 0
        if np.abs(x-solsx[0]) > np.abs(x-solsx[1]):
            closex = solsx[1]
        else:
            closex = solsx[0]
        #finding the zeros of the y values   
        Ay = 1
        By = -2*yc
        Cy = yc**2+(closex-xc)**2-R**2
        coeffy = [Ay,By,Cy]
        solsy = np.roots(coeffy)
        if np.abs(y-solsy[0]) > np.abs(y-solsy[1]):
            closey = solsy[1]
        else:
            closey = solsy[0]

        self.ax1.plot([x,closex],[y,closey],'g')
        
        offset = [x-closex,y-closey]
        return offset
        
        
