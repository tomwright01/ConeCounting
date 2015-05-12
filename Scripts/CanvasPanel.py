import wx
import numpy as np
import logging
import matplotlib
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.figure import Figure

logger = logging.getLogger('ConeCounter.CanvasPanel')

class CanvasPanel(wx.Panel):
    """This is a wx.panel that will hold a matplotlib canvas"""
    
    axis_limits=None
    
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        #Setup the drawing surface
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        

        #Add a standard navigation toolbar
        toolbar = NavigationToolbar(self.canvas)
        
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(toolbar)
        self.SetSizer(sizer)

    def on_axes_changed(self,event):
        logger.debug('axes change fired')
        self.axis_limits = self.axes.axis()
        

        
    def draw(self,image=None):
        """Draw an image onto the canvas"""
        if image is None:
            #Plot a simple numpy square is nothing is passed
            self.axes.imshow(np.ones((5,5)))
            return
        self.axes.clear()
        self.axes.imshow(image)
            
        #Bind an event to the axes so I can update when the image is zoomed
        cid = self.axes.callbacks.connect('xlim_changed',self.on_axes_changed)
        cid = self.axes.callbacks.connect('ylim_changed',self.on_axes_changed)
        if not self.axis_limits is None:
            self.axes.axis(self.axis_limits)
        self.canvas.draw()

    def getAxesLimits(self):
        """Get the current limits of the axes"""

