#!/usr/bin/ python
"""
User interface for creating instrument block data.
"""
import os, time, subprocess
import wx
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

    def create_main_panel(self):
      self.panel = wx.Panel(self)

      self.pathText=wx.StaticText(self.panel, label='Path: ')
      self.inPath=wx.TextCtrl(self.panel, size=(500, 20))

      self.inPath.SetValue('/Users/jwhueh/projects/SDSS/InstBlock/grid.dat')

      self.gridButton = wx.Button(self.panel, label='Fit Scale && Orientation')
      self.Bind(wx.EVT_BUTTON,self.test, self.gridButton)

      self.xLabel = wx.StaticText(self.panel, label='X', pos=(273,78))
      self.yLabel = wx.StaticText(self.panel, label='Y', pos=(323,78))

      self.binFactor = wx.StaticText(self.panel, label='Bin Factor')
      self.binX = wx.TextCtrl(self.panel,size=(50,-1), value='2')
      self.binY = wx.TextCtrl(self.panel,size=(50,-1), value='3')

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

      self.oldRot = wx.StaticText(self.panel, label='Old Rotation Instrument Angle')
      self.oldRotDeg = wx.TextCtrl(self.panel, size=(100,-1))
      self.oldRotLabel = wx.StaticText(self.panel, label='deg')
      self.newRot = wx.StaticText(self.panel, label='New Rotation Instrument Angle')
      self.newRotDeg = wx.TextCtrl(self.panel, size=(100,-1))
      self.newRotLabel = wx.StaticText(self.panel, label='deg')

      self.xLabel2 = wx.StaticText(self.panel, label='X', pos=(300,328))
      self.yLabel2 = wx.StaticText(self.panel, label='Y', pos=(400,328))

      self.oldRotXY = wx.StaticText(self.panel, label='Old Rotation Instrument Coordinates')
      self.oldRotX = wx.TextCtrl(self.panel, size=(100,-1))
      self.oldRotY = wx.TextCtrl(self.panel, size=(100,-1))
      self.oldRotSkyDegLabel = wx.StaticText(self.panel, label='deg on sky')
      self.newRotXY = wx.StaticText(self.panel, label='New Rotation Instrument Coordinates')
      self.newRotX = wx.TextCtrl(self.panel, size=(100,-1))
      self.newRotY = wx.TextCtrl(self.panel, size=(100,-1))
      self.newRotSkyDegLabel = wx.StaticText(self.panel, label='deg on sky')

      self.noteToUser = wx.StaticText(self.panel, label='If this instrument is also a full-frame guider (the whole CCD is one probe),\n e.g., 3.5m NA2 guider, then...')

      self.newGPRot = wx.StaticText(self.panel, label='New Guider Position Rotation Coordinates')
      self.newGPRotX = wx.TextCtrl(self.panel, size=(100,-1))
      self.newGPRotY = wx.TextCtrl(self.panel, size=(100,-1))
      self.newGPRotLabel = wx.StaticText(self.panel, label='deg on sky')
      
      self.comboLabel = wx.StaticText(self.panel, label='Type of Data')
      self.combo=wx.ComboBox(self.panel,-1,choices=['Guider','Instrument'],style=wx.CB_READONLY)
      self.Bind(wx.EVT_COMBOBOX, self.dataTypeSelect, self.combo)
      
      self.fitButton = wx.Button(self.panel, label='Fit Position')
      self.Bind(wx.EVT_BUTTON, self.onFitPos, self.fitButton)

      self.log=wx.TextCtrl(self.panel,size=(400,200),style=wx.TE_MULTILINE)

      #defining horizontal sizers
      self.topSizer=wx.BoxSizer(wx.VERTICAL)
      self.pathSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.comboSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.binSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.imSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.logSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.regionSizer=wx.GridSizer(2,4,3,3)
    
      self.checkSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.im2Sizer=wx.BoxSizer(wx.HORIZONTAL)
      self.oldRotSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.newRotSizer=wx.BoxSizer(wx.HORIZONTAL)
      
      self.oldRotXYSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.newRotXYSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.newGPSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.noteSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.fitButtonSizer=wx.BoxSizer(wx.HORIZONTAL)
      self.fitSclSizer=wx.BoxSizer(wx.HORIZONTAL)

      #adding parts to horizontal sizers
      self.pathSizer.Add(self.pathText,0,wx.EXPAND)
      self.pathSizer.Add(self.inPath,0,wx.EXPAND)

      self.comboSizer.Add(self.comboLabel,0,wx.EXPAND)
      self.comboSizer.Add(self.combo,0,wx.EXPAND)

      self.binSizer.Add(self.binFactor,0,wx.EXPAND)
      self.binSizer.Add(self.binX,0,wx.EXPAND)
      self.binSizer.Add(self.binY,0,wx.EXPAND)
      
      self.imSizer.Add(self.imCtr,0,wx.EXPAND)
      self.imSizer.Add(self.imCtrX,0,wx.EXPAND)
      self.imSizer.Add(self.imCtrY,0,wx.EXPAND)
      self.imSizer.Add(self.imCtrPix,0,wx.EXPAND)

      self.im2Sizer.Add(self.imScl,0,wx.EXPAND)
      self.im2Sizer.Add(self.imSclX,0,wx.EXPAND)
      self.im2Sizer.Add(self.imSclY,0,wx.EXPAND)
      self.im2Sizer.Add(self.imSclPixDeg,0,wx.EXPAND)

      self.checkSizer.Add(self.aspectRatioBox,0,wx.EXPAND)
      self.checkSizer.Add(self.aspectLabel,0,wx.EXPAND)

      self.oldRotSizer.Add(self.oldRot,0,wx.EXPAND)
      self.oldRotSizer.Add(self.oldRotDeg,0,wx.EXPAND)
      self.oldRotSizer.Add(self.oldRotLabel,0,wx.EXPAND)
      self.newRotSizer.Add(self.newRot,0,wx.EXPAND)
      self.newRotSizer.Add(self.newRotDeg,0,wx.EXPAND)
      self.newRotSizer.Add(self.newRotLabel,0,wx.EXPAND)

      self.fitSclSizer.Add(self.gridButton,0,wx.EXPAND)

      self.oldRotXYSizer.Add(self.oldRotXY,0,wx.EXPAND)
      self.oldRotXYSizer.Add(self.oldRotX,0,wx.EXPAND)
      self.oldRotXYSizer.Add(self.oldRotY,0,wx.EXPAND)
      self.oldRotXYSizer.Add(self.oldRotSkyDegLabel,0,wx.EXPAND)

      self.newRotXYSizer.Add(self.newRotXY,0,wx.EXPAND)
      self.newRotXYSizer.Add(self.newRotX,0,wx.EXPAND)
      self.newRotXYSizer.Add(self.newRotY,0,wx.EXPAND)
      self.newRotXYSizer.Add(self.newRotSkyDegLabel,0,wx.EXPAND)

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
      self.topSizer.AddSpacer(10)
      self.topSizer.Add(self.comboSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(20)
      self.topSizer.AddSpacer(5)
      self.topSizer.Add(self.binSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(10)
      self.topSizer.Add(self.imSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(10)
      self.topSizer.Add(self.im2Sizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(5)
      self.topSizer.Add(self.checkSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(15)
      self.topSizer.Add(self.oldRotSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(10)
      self.topSizer.Add(self.newRotSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(10)
      self.topSizer.Add(self.fitSclSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(30)
      self.topSizer.Add(self.oldRotXYSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(5)
      self.topSizer.Add(self.newRotXYSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(25)
      self.topSizer.Add(self.noteSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(25)
      self.topSizer.Add(self.newGPSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(5)
      self.topSizer.Add(self.fitButtonSizer,0,wx.ALIGN_CENTER)
      self.topSizer.AddSpacer(5)
      self.topSizer.Add(self.logSizer,0,wx.ALIGN_CENTER)
      
      self.panel.SetSizer(self.topSizer)
      self.topSizer.Fit(self)
      

    def onExit(self,event):
        self.Close(True)

    def onAbout(self, event):
        dlg=wx.MessageDialog(self,'SDSS Instrument Block Fitter\n'                    
                             ,'About', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def test(self,event):
        print 'a button was pressed'
        return

    def dataTypeSelect(self,event):
        print "data type selected"
        return

    def aspectCheck(self,event):
        print "aspect ratio box checked"
        return
    
    def onFitPos(self,event):
        print "Fit Position button clicked"
        return

    
if __name__=="__main__":
  app = wx.App()
  app.frame = InstBlock(None, 'SDSS Instrument Block')
  app.frame.Show()
  app.MainLoop()
