import numpy as np
import matplotlib
import os

matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import wx

class ControlPanel(wx.Panel):
    """A wx.panel to hold the main gui controls"""
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        
        #add some buttons, they dont do anything yet
        self.sizer = wx.GridBagSizer(vgap=5,hgap=5)
        self.buttons = []
        for i in range(0, 6):
            self.buttons.append(wx.Button(self, -1, "Button &"+str(i)))
            self.sizer.Add(self.buttons[i], pos=(i,0))       

        self.labels = []
        for i in range(0, 6):
            self.labels.append(wx.StaticText(self, label="Label &"+str(i)))
            self.sizer.Add(self.labels[i], pos=(i,1))        

            
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

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
        
    def draw(self):
        """Put a basic sine wave on"""
        t = np.arange(0.0,3.0,0.01)
        s = np.sin(2 * np.pi * t)
        self.axes.plot(t,s)

class MyFrame(wx.Frame):
    """This will be the main window"""
    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,title=title,size=(800,600))
        self.image = CanvasPanel(self) # the canvas for image display
        self.controls = ControlPanel(self) # the control buttons
        self.image.draw()
        
        self.CreateStatusBar() # A Statusbar in the bottom of the window
        
        # Setting up the menu
        filemenu = wx.Menu()
        menuItem_fileopen = filemenu.Append(wx.ID_OPEN,"&0pen"," Open source file")
        filemenu.AppendSeparator()
        menuItem_about = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        filemenu.AppendSeparator()
        menuItem_exit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        
        
        self.Bind(wx.EVT_MENU,self.OnOpen,menuItem_fileopen)
        self.Bind(wx.EVT_MENU,self.onAbout,menuItem_about)
        self.Bind(wx.EVT_MENU,self.onExit,menuItem_exit)
        
        #Creating the menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") #adding the filemenu to the menubar
        self.SetMenuBar(menuBar)
        
        #setup the layout
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.image, 2, wx.EXPAND)
        self.sizer.Add(self.controls, 1, wx.EXPAND)
        
        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        
        self.Show(True)
    
    def onAbout(self, event):
        """callback for menuitem_about"""
        dlg = wx.MessageDialog( self, "A small app in wxPython", "ConeCounter", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def onExit(self, event):
        """callback for menuitem_exit"""
        self.Close(True)
        
    def OnOpen(self, event):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            #self.control.SetValue(f.read())
            f.close()
        dlg.Destroy()    
    
if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame(None,'ConeCounter')
    app.MainLoop()