#! /usr/bin/ python
import os, time, re, time, subprocess, wx, thread
import instcalc
import dateutil
import scipy
from scipy import stats
import numpy as np
import pyfits
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
import matplotlib.dates as dt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
__author__ = "Joseph Huehnerhoff"
__date__="Date: 2015/05/12"
"""
Usage:  python InstBuild.py
Build:  rm -rf build dist
        python setup.py py2app -p wx
"""

class InstBlock(wx.Frame):
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, None, -1,title)

        self.current=None
        self.xmin=0
        self.xmax=0
        self.ymin=0
        self.ymax=0
        
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()
 
    
    def create_menu(self):
      self.menubar = wx.MenuBar()
 
      menu_file = wx.Menu()
      m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
      self.Bind(wx.EVT_MENU, self.onExit, m_exit)
      
      m_about = menu_file.Append(-1, "&About\tF1", "About SDSS Inst Block")
      self.Bind(wx.EVT_MENU, self.onAbout, m_about)
      
      self.menubar.Append(menu_file, "&File")
      
      self.SetMenuBar(self.menubar)

    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    #defining all the elements of the main panel, text boxes, buttons, etc.
    def create_main_panel(self):
      self.panel = wx.Panel(self)

      #creating the matplotlib portion of the panel
      self.dpi = 100
      self.fig = Figure((9, 8), dpi=self.dpi)
      self.canvas = FigCanvas(self.panel,-1,self.fig)
      
      #end of matplotlib section

      self.pathText=wx.StaticText(self.panel, label='ring path: ')
      self.inPath=wx.TextCtrl(self.panel, size=(500, 20),style=wx.TE_PROCESS_ENTER)
      self.inPath.SetValue('/Users/jwhueh/Caitlin/InstrumentBlockGUI/110318_agile_ring.txt')

      self.fitButton = wx.Button(self.panel, label='Fit Position')
      self.Bind(wx.EVT_BUTTON, self.fileRead, self.fitButton)

      self.path2Text=wx.StaticText(self.panel,label='grid path: ')
      self.inPath2=wx.TextCtrl(self.panel, size=(500,20),style=wx.TE_PROCESS_ENTER)
      self.inPath2.SetValue('/Users/jwhueh/Caitlin/InstrumentBlockGUI/110318_agile_grid.txt')
      
      self.gridButton = wx.Button(self.panel, label='Fit Scale && Orientation')
      self.Bind(wx.EVT_BUTTON,self.fileRead, self.gridButton)

      self.empty1 = wx.StaticText(self.panel)
      self.xLabel = wx.StaticText(self.panel, label='X')
      self.yLabel = wx.StaticText(self.panel, label='Y')
      self.empty2 = wx.StaticText(self.panel)

      self.binFactor = wx.StaticText(self.panel, label='Bin Factor')
      self.binX = wx.TextCtrl(self.panel,size=(50,-1), value='2')
      self.binY = wx.TextCtrl(self.panel,size=(50,-1), value='3')
      self.empty3 = wx.StaticText(self.panel)

      self.imCtr = wx.StaticText(self.panel, label='Image Center')
      self.imCtrX = wx.TextCtrl(self.panel,size=(100,-1))
      self.imCtrY = wx.TextCtrl(self.panel,size=(100,-1))
      self.imCtrPix = wx.StaticText(self.panel, label='unbinned pixels')

      self.imScl = wx.StaticText(self.panel, label='Image Scale')
      self.imSclX = wx.TextCtrl(self.panel, size=(100,-1))
      self.imSclY = wx.TextCtrl(self.panel, size=(100,-1))
      self.imSclPixDeg = wx.StaticText(self.panel, label='unbinned pix/deg')

      self.aspectLabel = wx.StaticText(self.panel, label='Aspect Ratio is Exact')
      self.aspectRatioBox = wx.CheckBox(self.panel,-1)
      self.aspectRatioBox.SetValue(True)
      self.Bind(wx.EVT_CHECKBOX, self.aspectCheck, self.aspectRatioBox)

      self.oldRot = wx.StaticText(self.panel, label='Prior Inst. Angle')
      self.oldRotDeg = wx.TextCtrl(self.panel, size=(100,-1))
      self.oldRotLabel = wx.StaticText(self.panel, label='deg')
      self.newRot = wx.StaticText(self.panel, label='New Inst. Angle')
      self.newRotDeg = wx.TextCtrl(self.panel, size=(100,-1))
      self.newRotLabel = wx.StaticText(self.panel, label='deg')

      self.empty4 = wx.StaticText(self.panel)
      self.xLabel2 = wx.StaticText(self.panel, label='X')
      self.yLabel2 = wx.StaticText(self.panel, label='Y')
      self.empty5 = wx.StaticText(self.panel)

      self.oldRotXY = wx.StaticText(self.panel, label='Prior Inst Coords')
      self.oldRotX = wx.TextCtrl(self.panel, size=(100,-1))
      self.oldRotY = wx.TextCtrl(self.panel, size=(100,-1))
      self.oldRotSkyDegLabel = wx.StaticText(self.panel, label='deg on sky')

      self.newRotXY = wx.StaticText(self.panel, label='New Inst Coords')
      self.newRotX = wx.TextCtrl(self.panel, size=(100,-1))
      self.newRotY = wx.TextCtrl(self.panel, size=(100,-1))
      self.newRotSkyDegLabel = wx.StaticText(self.panel, label='deg on sky')

      self.noteToUser = wx.StaticText(self.panel, label='If this instrument is also a full-frame guider (the whole CCD is one probe),\n e.g., 3.5m NA2 guider, then...')

      self.newGPRot = wx.StaticText(self.panel, label='New Guider Coords')
      self.newGPRotX = wx.TextCtrl(self.panel, size=(100,-1))
      self.newGPRotY = wx.TextCtrl(self.panel, size=(100,-1))
      self.newGPRotLabel = wx.StaticText(self.panel, label='deg on sky')
      
      self.comboLabel = wx.StaticText(self.panel, label='Type of Data')
      self.combo=wx.ComboBox(self.panel,-1,choices=['Guider','Instrument'],style=wx.CB_READONLY)
      self.Bind(wx.EVT_COMBOBOX, self.dataTypeSelect, self.combo)
      
      self.log=wx.TextCtrl(self.panel,size=(400,200),style=wx.TE_MULTILINE)

      #defining horizontal sizers
      self.mainSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.topSizer=wx.BoxSizer(wx.VERTICAL)
      self.top2Sizer=wx.BoxSizer(wx.VERTICAL)
      self.pathSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.path2Sizer=wx.BoxSizer(wx.HORIZONTAL)
      self.comboSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.logSizer=wx.BoxSizer(wx.HORIZONTAL)

      self.imageSizer=wx.GridSizer(rows=4,cols=4,hgap=5,vgap=5)
      self.regionSizer=wx.GridSizer(2,4,3,3)
    
      self.checkSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.oldRotSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.newRotSizer=wx.BoxSizer(wx.HORIZONTAL)
      
      self.rotXYSizer=wx.GridSizer(rows=3,cols=4,hgap=5,vgap=5)
      self.newGPSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.noteSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.fitButtonSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.fitSclSizer=wx.BoxSizer(wx.HORIZONTAL)

      #adding parts to horizontal sizers
      self.pathSizer.Add(self.pathText,0,wx.EXPAND)
      self.pathSizer.Add(self.inPath,0,wx.EXPAND)
      
      self.path2Sizer.Add(self.path2Text,0,wx.EXPAND)
      self.path2Sizer.Add(self.inPath2,0,wx.EXPAND)

      self.comboSizer.Add(self.comboLabel,0,wx.EXPAND)
      self.comboSizer.Add(self.combo,0)

      self.imageSizer.Add(self.empty1,0,wx.EXPAND)
      self.imageSizer.Add(self.xLabel,0,wx.ALIGN_CENTER)
      self.imageSizer.Add(self.yLabel,0,wx.ALIGN_CENTER)
      self.imageSizer.Add(self.empty2,0,wx.EXPAND)

      self.imageSizer.Add(self.binFactor,0,wx.ALIGN_RIGHT)
      self.imageSizer.Add(self.binX,0,wx.ALIGN_CENTER)
      self.imageSizer.Add(self.binY,0,wx.ALIGN_CENTER)
      self.imageSizer.Add(self.empty3,0,wx.ALIGN_RIGHT)
      
      self.imageSizer.Add(self.imCtr,0,wx.ALIGN_RIGHT)
      self.imageSizer.Add(self.imCtrX,0,wx.ALIGN_CENTER)
      self.imageSizer.Add(self.imCtrY,0,wx.ALIGN_CENTER)
      self.imageSizer.Add(self.imCtrPix,0,wx.ALIGN_LEFT)

      self.imageSizer.Add(self.imScl,0,wx.ALIGN_RIGHT)
      self.imageSizer.Add(self.imSclX,0,wx.ALIGN_CENTER)
      self.imageSizer.Add(self.imSclY,0,wx.ALIGN_CENTER)
      self.imageSizer.Add(self.imSclPixDeg,0,wx.ALIGN_LEFT)
      

      self.checkSizer.Add(self.aspectRatioBox,0,wx.EXPAND)
      self.checkSizer.Add(self.aspectLabel,0,wx.EXPAND)

      self.oldRotSizer.Add(self.oldRot,0,wx.EXPAND)
      self.oldRotSizer.Add(self.oldRotDeg,0,wx.EXPAND)
      self.oldRotSizer.Add(self.oldRotLabel,0,wx.EXPAND)
      self.newRotSizer.Add(self.newRot,0,wx.EXPAND)
      self.newRotSizer.Add(self.newRotDeg,0,wx.EXPAND)
      self.newRotSizer.Add(self.newRotLabel,0,wx.EXPAND)

      self.fitSclSizer.Add(self.gridButton,0,wx.EXPAND)

      self.rotXYSizer.Add(self.empty4,0,wx.EXPAND)
      self.rotXYSizer.Add(self.xLabel2,0,wx.ALIGN_CENTER)
      self.rotXYSizer.Add(self.yLabel2,0,wx.ALIGN_CENTER)
      self.rotXYSizer.Add(self.empty5,0,wx.EXPAND)
      
      self.rotXYSizer.Add(self.oldRotXY,0,wx.ALIGN_RIGHT)
      self.rotXYSizer.Add(self.oldRotX,0,wx.ALIGN_CENTER)
      self.rotXYSizer.Add(self.oldRotY,0,wx.ALIGN_CENTER)
      self.rotXYSizer.Add(self.oldRotSkyDegLabel,0,wx.ALIGN_LEFT)

      self.rotXYSizer.Add(self.newRotXY,0,wx.ALIGN_RIGHT)
      self.rotXYSizer.Add(self.newRotX,0,wx.ALIGN_CENTER)
      self.rotXYSizer.Add(self.newRotY,0,wx.ALIGN_CENTER)
      self.rotXYSizer.Add(self.newRotSkyDegLabel,0,wx.ALIGN_LEFT)

      self.newGPSizer.Add(self.newGPRot,0,wx.EXPAND)
      self.newGPSizer.Add(self.newGPRotX,0,wx.EXPAND)
      self.newGPSizer.Add(self.newGPRotY,0,wx.EXPAND)
      self.newGPSizer.Add(self.newGPRotLabel,0,wx.EXPAND)

      self.noteSizer.Add(self.noteToUser,0,wx.EXPAND)

      self.fitButtonSizer.Add(self.fitButton,0,wx.EXPAND)
      self.logSizer.Add(self.log,0,wx.EXPAND)

  
      #fitting everything in the vertical sizer
      self.topSizer.AddSpacer(15)
      self.topSizer.Add(self.pathSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(5)
      self.topSizer.Add(self.path2Sizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(10)
      self.topSizer.Add(self.comboSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(15)
      self.topSizer.Add(self.imageSizer,0,wx.ALIGN_RIGHT)
      self.topSizer.AddSpacer(10)
      self.topSizer.Add(self.checkSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(15)
      self.topSizer.Add(self.oldRotSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(10)
      self.topSizer.Add(self.newRotSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(10)
      self.topSizer.Add(self.fitSclSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(10)
      self.topSizer.Add(self.rotXYSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(25)
      self.topSizer.Add(self.noteSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(25)
      self.topSizer.Add(self.newGPSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(5)
      self.topSizer.Add(self.fitButtonSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(5)
      self.topSizer.Add(self.logSizer,0,wx.ALIGN_CENTER)      
      self.top2Sizer.Add(self.canvas,0,wx.ALIGN_CENTER)
      self.mainSizer.Add(self.topSizer,0)
      self.mainSizer.AddSpacer(100)
      self.mainSizer.Add(self.top2Sizer,0)
      
      self.panel.SetSizer(self.mainSizer)
      self.mainSizer.Fit(self)
      
    def onAbout(self,event):
        dlg=wx.MessageDialog(self,'DIS Linearity Analysis\n', 'About', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        return

    def onExit(self,event):
        self.Close(True)

    def dataTypeSelect(self,event):
        print "data type selected"
        return

    def aspectCheck(self,event):
        print "aspect ratio box checked"
        return
    
    def on_graph_button(self,event):
        print "clicked graph button"
        return

    #takes event from user entered file, takes coordinates from given file
    def fileRead(self,event):
        dataRing = True
        if event.GetId() == -2019:
            dataRing = False

        if dataRing == True:
            filename = self.inPath.GetValue()
        else:
            filename=self.inPath2.GetValue()

        file = open(filename,'r')
        line = file.readline().lstrip()
        #first two columns of the grid file
        first = []
        second = []
        #end of first two columns
        x_coo = []
        y_coo = []
        
        while line:
            line_seg = line.split()

            if dataRing == False:
                first.append(float(line_seg[0]))
                second.append(float(line_seg[1]))
                x_coo.append(float(line_seg[2]))
                y_coo.append(float(line_seg[3]))
            else:
                x_coo.append(float(line_seg[1]))
                y_coo.append(float(line_seg[2]))
            line = file.readline().lstrip()

        file.close()
        
        if dataRing == True:
            object = [x_coo,y_coo]
            graphing = instcalc.BoresightData(object)
            circleInfo = graphing.boresightPos()
            self.graphRing(circleInfo,object)
        else:
            object = [first,second,x_coo,y_coo]
            graphing = instcalc.GridData(object,2)
            slope_list,yint_list = graphing.rotationAngle()
            self.graphGridData(object,slope_list,yint_list)
            return

    def graphGridData(self,object,slope_list,yint_list):
        self.ax1 = self.fig.add_subplot(211)
        self.ax1.clear()
        self.ax1.set_title('Grid')
        self.ax1.set_ylabel('y')
        self.ax1.set_xlabel('x')
        self.ax1.plot(object[2],object[3],'o',clip_on=False,ms=2)

        #plots the fit of each grid line
        for i in range(len(slope_list)):
            y = range(int(min(object[3])),int(max(object[3])))
            x = []
            for j in range(len(y)):
                x.append((y[j]-yint_list[i])/slope_list[i])
            self.ax1.plot(x,y)
            self.ax1.annotate('rotAng = %.2f'%(slope_list[i]),(min(x),min(y)),fontsize=8)
        self.ax1.set_aspect('equal',adjustable='box')
        self.canvas.draw()
        return

#graphs the data points taken from the file, plots the centerpoint and circle estimate, calls to nearCircle to 
#calculate and display the offset
    def graphRing(self,circleInfo,object):
        self.ax1 = self.fig.add_subplot(212)
        self.ax1.clear()
        self.ax1.set_title('Ring')
        self.ax1.set_ylabel('y')
        self.ax1.set_xlabel('x')
        self.ax1.plot(object[0],object[1],'o',clip_on=False,ms=2)
        self.ax1.plot(circleInfo[0],circleInfo[1],'ro')
        circle = plt.Circle((circleInfo[0],circleInfo[1]),circleInfo[2],color='r',fill=False)
        self.ax1.add_artist(circle)
        self.ax1.set_aspect('equal',adjustable='box')
        for i in range(len(object[0])):
            offset = self.nearCircle(object[0][i],object[1][i],circleInfo[0],circleInfo[1],circleInfo[2])
            self.ax1.annotate('(%.2f,%.2f)'%(offset[0],offset[1]),(object[0][i]+5,object[1][i]+5),fontsize=8)
        self.canvas.draw()
        return

    #defines the line y = mx+b connecting the given data point (x,y) and the circle's centerpoint (xc,yc) then
    #defines circle using centerpoint and radius, finds intersections of the circle and the line
    #and selects the nearest one, with A, B, and C being the points in the quadratic equation 
    def nearCircle(self,x,y,xc,yc,R):
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
            
if __name__=="__main__":
  app = wx.App()
  app.frame = InstBlock(None, 'SDSS Instrument Block')
  app.frame.Show()
  app.MainLoop()
