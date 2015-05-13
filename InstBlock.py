#!/usr/bin/env python
"""
User interface for creating instrument block data.
"""
import os, time, re, subprocess, wx, thread
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
        wx.Frame.__init__(self, None, -1, title)

        self.current = None
        self.xmin =0
        self.xmax=0
        self.ymin=0
        self.ymax=0

        self.unusable=None
        
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

        self.gridButton = wx.Button(self.panel, label='Fit Scale & Orientation')
        self.Bind(wx.EVT_BUTTON,self.test, self.gridButton)

        self.binFactor = wx.StaticText(self.panel, label='Bin Factor')
        self.binX = wx.TextCtrl(self.panel,size=(50,-1))
        self.binY = wx.TextCtrl(self.panel,size=(50,-1))

        self.imCtr = wx.StaticText(self.panel, label='Image Center')
        self.imCtrX = wx.TextCtrl(self.panel,size=(100,-1))
        self.imCtrY = wx.TextCtrl(self.panel,size=(100,-1))
        self.imCtrPix = wx.StaticText(self.panel, label='unbinned pixels')
      
        #self.combo=wx.ComboBox(self.panel,-1,choices=['Red','Blue'],style=wx.CB_READONLY)
     
      
     
        self.log=wx.TextCtrl(self.panel,size=(400,200),style=wx.TE_MULTILINE)

        self.topSizer=wx.BoxSizer(wx.VERTICAL)
        self.pathSizer=wx.BoxSizer(wx.HORIZONTAL)
        self.binSizer=wx.BoxSizer(wx.HORIZONTAL)
        self.imSizer=wx.BoxSizer(wx.HORIZONTAL)
        self.comboSizer=wx.BoxSizer(wx.HORIZONTAL)
        self.logSizer=wx.BoxSizer(wx.HORIZONTAL)
        self.regionSizer=wx.GridSizer(2,4,3,3)
      
        self.pathSizer.Add(self.pathText,0,wx.EXPAND)
        self.pathSizer.Add(self.inPath,0,wx.EXPAND)
        self.pathSizer.Add(self.gridButton,0,wx.EXPAND)

        self.binSizer.Add(self.binFactor,0,wx.EXPAND)
        self.binSizer.Add(self.binX,0,wx.EXPAND)
        self.binSizer.Add(self.binY,0,wx.EXPAND)

        self.imSizer.Add(self.imCtr,0,wx.EXPAND)
        self.imSizer.Add(self.imCtrX,0,wx.EXPAND)
        self.imSizer.Add(self.imCtrY,0,wx.EXPAND)
        self.imSizer.Add(self.imCtrPix,0,wx.EXPAND)

        self.logSizer.Add(self.log,0,wx.EXPAND)
  
        self.topSizer.AddSpacer(10)
        self.topSizer.Add(self.pathSizer,0,wx.EXPAND)
        self.topSizer.AddSpacer(5)
        self.topSizer.Add(self.binSizer,0,wx.ALIGN_CENTER)
        self.topSizer.AddSpacer(10)
        self.topSizer.Add(self.imSizer,0,wx.ALIGN_CENTER)
        self.topSizer.AddSpacer(5)
        self.topSizer.Add(self.logSizer,0,wx.EXPAND)
     
        self.panel.SetSizer(self.topSizer)
        self.topSizer.Fit(self)
      

    def onExit(self,event):
        self.Close(True)

    def onAbout(self, event):
        dlg=wx.MessageDialog(self,'DIS Linearity Analysis\n'                    
                             ,'About', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def test(self,event):
        print 'a button was pressed'
        return

    def runBias(self,event):
        thread.start_new_thread(self.makeBias,())

    def makeBias(self):
      wx.CallAfter(self.log.AppendText,'-------------------\n')
      wx.CallAfter(self.log.AppendText,'Making Bias\n')
      arr=[]
      path=self.inPath.GetValue()
      camera=self.combo.GetValue()
      if camera == 'Blue':
          c='b'
      else:
          c='r'
      files=subprocess.Popen(['ls',path],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
      p=files.stdout.readlines()
      for im in p:
          im=im.rstrip('\n')
          if re.search('dis_bias',im) and re.search(c+'.fits',im):
              wx.CallAfter(self.log.AppendText,im+'\n')
              arr.append(path+im)
      biasData=np.array([pyfits.getdata(d) for d in arr])
      bias=biasData.mean(axis=0)
      dataHdr=pyfits.getheader(arr[0])
      hdu=pyfits.PrimaryHDU(bias,dataHdr)
      bias_name='bias_avg_'+c+'.fits'
      if os.path.exists(path+bias_name):
          os.system('rm '+path+bias_name)
      master_stat=np.mean(bias[200:len(bias)-200,200:len(bias[0])-200])
      hdu.writeto(path+bias_name)
      wx.CallAfter(self.log.AppendText,'Master Bias Created\n')
      wx.CallAfter(self.log.AppendText,str(bias_name) +':  ' + str(master_stat)+'\n')
      
    def runRN(self):
        thread.start_new_thread(self.calcRN,())

    def calcRN(self, event):
        arr=[]
        wx.CallAfter(self.log.AppendText,'-------------------\n')
        wx.CallAfter(self.log.AppendText,'Calculating Read Noise\n')
        path=self.inPath.GetValue()
        camera=self.combo.GetValue()
        if camera == 'Blue':
            c='b'
        else:
            c='r'
        master_name=path+'bias_avg_'+c+'.fits'
        master_bias=pyfits.getdata(master_name)

        files=subprocess.Popen(['ls',path],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p=files.stdout.readlines()
        wx.CallAfter(self.log.AppendText,'Taking Difference Image of Master Bias - Single Bias\n')
        wx.CallAfter(self.log.AppendText,'mean       stdev       RN(ADUs)\n')
        for im in p:
            im=im.rstrip('\n')
            if re.search('dis_bias',im) and re.search(c+'.fits',im):
                bias_name=path+im
                bias_temp=pyfits.getdata(bias_name)
                diff_bias=bias_temp-master_bias
                stdev_diff=np.std(diff_bias[200:len(master_bias)-200,200:len(master_bias[0])-200])
                mean_diff=np.mean(diff_bias[200:len(master_bias)-200,200:len(master_bias[0])-200])
                rn=stdev_diff/np.sqrt(2.0)
                arr.append(rn)
                wx.CallAfter(self.log.AppendText,('%.3f      %.3f     %.3f\n') % (mean_diff, stdev_diff, rn))
        wx.CallAfter(self.log.AppendText,'Average Read Noise: %.3f \n'%np.mean(rn))
      
    def startRun(self,event):
      thread.start_new_thread(self.run,())

    def run(self):
      wx.CallAfter(self.log2.AppendText,'Slope       Intercept       r^2     Gain\n')
      wx.CallAfter(self.log.AppendText,'Image        Adjusted Mean      Raw Mean\n')
      path=self.inPath.GetValue()
      #dt=None #'UTC' or None depending on type of linearity plot
      
      camera=self.combo.GetValue()
      
      if camera=='Blue':
        cabrev='b'
        cdraw='b.'
        cdrawb='bx'
      else:
        cabrev='r'
        cdraw='r.'
        cdrawb='rx'
      ima=path+'bias_avg_'+cabrev+'.fits'
      hdulist=pyfits.open(ima)
      binx=hdulist[0].header['CCDBIN1']
      biny=hdulist[0].header['CCDBIN2']
      hdulist.close()
      self.xmin=int(self.xminIn.GetValue())
      self.xmax=int(self.xmaxIn.GetValue())
      self.ymin=int(self.yminIn.GetValue())
      self.ymax=int(self.ymaxIn.GetValue())
      self.fig.clf()
      self.axes.clear()
      self.fig.text(.3,.91,'Linearity', size='x-small')
      self.fig.text(.7,.91,'Control', size='x-small')
      self.fig.text(.45,.47,'Transfer Efficiency', size='x-small')
      region='['+str(self.xmin)+':'+str(self.xmax)+','+str(self.ymin)+':'+str(self.ymax)+']'
      self.fig.text(.2,.95, 'DIS '+camera+' Statistics: sampling region: '+ region+', binning: '+ str(binx)+'x'+str(biny), size='small')
      linarrx=[]
      linarry=[]
      linarry_raw=[]
      conarrx=[]
      conarry=[]
      tearrx=[]
      tearry=[]
      linarrr=[1,1]
      linarrte=[]
      lintarrte=[]
      bestm=0
      bestb=0
      bestr=0
      controlarr=[]
      controlind=[]
      control_avg=0
      ratio_light=1
      files=subprocess.Popen(['ls',path],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
      p=files.stdout.readlines()
      for f in p:
        added=[]
        added.append(f.rstrip('\n'))
        if added  and re.search('bias',added[0])==None and re.search('.fits',added[0])!=None and re.search(cabrev+'.fits',added[0]):
              wx.CallAfter(self.log.AppendText,'Added: '+added[0])
              #perform image statistics on (???posibly bias subtraction)
              im=pyfits.open(path+added[0])
              sd=im[0].data[self.ymin:self.ymax, self.xmin:self.xmax]
              stats=np.mean(sd)

              self.ax1=self.fig.add_subplot(221)
              self.ax1.set_ylabel('counts', size='x-small')

              #------Plot ExpTime vs Counts----------
              if re.search('Control',added[0])==None:
                      
                      for num in controlind:
                        new=added[0][8:12]
                        if int(new)+1==int(num) or int(new)+2==int(num):
                          conexp= controlarr[controlind.index(num)]
                      ratio_light=float(conexp)/float(control_avg) 
                      self.ax1.set_xlabel('exposure time (seconds)', size='x-small')
                      linarrx.append(im[0].header['EXPTIME'])
                      linarry.append(float(stats)/ratio_light)
                      linarry_raw.append(float(stats))
                      wx.CallAfter(self.log.AppendText,'    %.2f    %.2f\n' % (stats, float(stats)/ratio_light))
                      self.ax1.plot(linarrx, linarry, cdraw)
                      self.ax1.plot(linarrx, linarry_raw,'g.')
                      for xlabel_i in self.ax1.get_xticklabels():
                        xlabel_i.set_fontsize(10)
                      for ylabel_i in self.ax1.get_yticklabels():
                        ylabel_i.set_fontsize(10)

                      #-------Calc linear regression----------
                      if len(linarrx) >2:
                              (gradient,intercept,r_value, p_value, std_err)=scipy.stats.linregress(linarrx,linarry)
                              linarrr.append(float(r_value**2))
                              #print r_value**2,float(stats[0])
                              q=open(path+'linfit.dat','a')
                              q.writelines(str(r_value**2)+'	'+str(gradient)+'	'+str(intercept)+'\n')
                              q.close()
                              self.canvas.draw()
                              #-------For plotting r^2 values----------
                              """polycoeffs=scipy.polyfit(linarrx, linarry,1)
                              yfit=scipy.polyval(polycoeffs, linarrx)
                              print yfit
                              pylab.plot(linarrx, yfit,'b')"""


                              """ax4=pylab.subplot(233)
                              ax4.yaxis.tick_left()

                              pylab.plot(lintarrte, linarrte, 'r.')	
                              pylab.xlabel('Exp Time (s)')
                              ax4=pylab.twinx()

                              pylab.plot(linarrx,linarrr, 'b.')
                              ax4.yaxis.tick_right()
                              pylab.draw()"""
              #--------plot control exposures---------
              self.ax3=self.fig.add_subplot(222)
              self.ax3.set_xlabel('UTC', size='x-small')
              if re.search('Control',added[0])!=None:
                wx.CallAfter(self.log.AppendText,'\n')
                controlarr.append(stats)
                controlind.append(added[0][11:15])
                dates1 = [matplotlib.dates.date2num(dateutil.parser.parse(im[0].header['UTC-OBS']))]
                self.ax3.plot(dates1, float(stats), cdraw)
                for xlabel_i in self.ax3.get_xticklabels():
                        xlabel_i.set_fontsize(10)
                for ylabel_i in self.ax3.get_yticklabels():
                        ylabel_i.set_fontsize(10)
                self.ax3.xaxis.set_major_locator(matplotlib.dates.MinuteLocator(interval=30))
                self.ax3.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
                locator=self.ax3.xaxis.get_major_locator()
                self.ax3.set_xlim(locator.autoscale())
                self.canvas.draw()
              control_avg=np.mean(controlarr)
              imanum=added[0].split('.')

              #--------plot transfer efficency curve--------
              self.ax2=self.fig.add_subplot(212)
              self.ax2.set_ylabel('variance', size='x-small')
              self.ax2.set_xlabel('counts', size='x-small')

              if imanum[0]==ima[0] and imanum[2]==ima[2] and (int(ima[1].rstrip(cabrev))+1)==int(imanum[1].rstrip(cabrev)):
                im1=path+ima[0]+'.'+ima[1]+'.'+ima[2]
                im1fits=pyfits.open(im1)
                im2=path+imanum[0]+'.'+imanum[1]+'.'+imanum[2]
                im2fits=pyfits.open(im2)
                imdiff=path+ima[0]+'.diff.'+ima[1]+'.'+ima[2]
                if len(ima)==3:
                  im1exp=im1fits[0].header['EXPTIME']
                  im2exp=im2fits[0].header['EXPTIME']

                  if im1exp==im2exp:
                    #Get a difference image while taking into account the ratio of the control light
                    diffTest=im1fits[0].data[self.ymin:self.ymax, self.xmin:self.xmax]/float(ratio_light)-im2fits[0].data[self.ymin:self.ymax, self.xmin:self.xmax]/float(ratio_light)
                    sigma=(float(np.std(diffTest))/(2**.5))**2
                    m1stat=np.mean(im1fits[0].data[self.ymin:self.ymax, self.xmin:self.xmax]/float(ratio_light))
                    m2stat=np.mean(im2fits[0].data[self.ymin:self.ymax, self.xmin:self.xmax]/float(ratio_light))
                    avg=(float(m1stat)+float(m2stat))/2
                    tearrx.append(avg)
                    tearry.append(sigma)
                    self.ax2.plot(tearrx, tearry,cdrawb)
                    for xlabel_i in self.ax2.get_xticklabels():
                        xlabel_i.set_fontsize(10)
                    for ylabel_i in self.ax2.get_yticklabels():
                        ylabel_i.set_fontsize(10)
                    self.canvas.draw()
                    f=open(path+'te.dat','a')
                    f.writelines(str(avg)+'	'+str(sigma)+'\n')
                    f.close()
                    (gradient,intercept,r_value, p_value, std_err)=scipy.stats.linregress(tearrx,tearry)
                    gain=1.0/gradient
                    wx.CallAfter(self.log2.AppendText,'%.3f     %.2f      %0.3f     %0.3f\n' % (gradient, intercept, r_value**2, gain))
                    if r_value**2 > bestr:
                      bestr=r_value**2
                      bestm=gradient
                      besty=intercept

                      if r_value**2 > .6:
                        linarrte.append(float(r_value**2))
                        lintarrte.append(float(im1exp))
                      w=open(path+'tefit.dat','a')
                      w.writelines(str(r_value**2)+'	'+str(gradient)+'	'+str(intercept)+'\n')
                      w.close()				

                      #print 'y='+ str(bestm)+'x + '+str(bestb)+' r^2= '+str(bestr)
                      """polycoeffs=scipy.polyfit(tearrx, tearry,1)
                      yfit=scipy.polyval(polycoeffs,tearrx)
                      pylab.plot(tearrx, yfit,'b')"""


                  im1fits.close()
                  im2fits.close()
              ima=imanum
              im.close()


              self.canvas.print_figure(path+'ccd_data_' + cabrev + '.png')
      
      wx.CallAfter(self.log.AppendText,'Plot Output: '+path+'ccd_data_' + cabrev + '.png\n'\
                          '------------------------\n')
      wx.CallAfter(self.log2.AppendText,'-----------------\n')

if __name__=="__main__":
  app = wx.App()
  app.frame = InstBlock(None, 'SDSS Instrument Block')
  app.frame.Show()
  app.MainLoop()
