import wx
import numpy as np
import matplotlib
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

class CanvasPanel(wx.Panel):
    """This is a wx.panel that will hold a matplotlib canvas"""
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()
        
    def draw(self,image=None):
        """Draw an image onto the canvas"""
        if image is None:
            #Plot a simple numpy square is nothing is passed
            self.axes.imshow(np.ones((5,5)))
            return
        self.axes.clear()
        self.axes.imshow(image)
        self.canvas.draw()
