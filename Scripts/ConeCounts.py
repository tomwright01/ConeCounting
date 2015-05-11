import numpy as np
import matplotlib
import os
import wx
import mahotas as mh
import logging

matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

class AOImage():
    """AO Image data
    Going to define this as a seperate class to hold all the image processing functions"""
    orgImage = None
    curImage = None
    
    def __init__(self,image=None):
        if image is not None:
            self.setOriginal(image)
        
    def getOriginal(self):
        return self.orgImage
    
    def getCurrent(self):
        #return the current image after any transformations have been applied
        return self.curImage
    
    def setOriginal(self,image):
        if not isinstance(image,np.ndarray):
            logger.error("Invalid image type: %s supplied",type(image))
            raise TypeError,"Invalid image supplied, expected ndarray"
        self.orgImage = image
        self.curImage = self.orgImage
                
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
        
    def draw(self,image=None):
        """Draw an image onto the canvas"""
        if image is None:
            #Plot a simple numpy square is nothing is passed
            self.axes.imshow(np.ones((5,5)))
            return
        self.axes.clear()
        self.axes.imshow(image)
        self.canvas.draw()
        

class MyFrame(wx.Frame):
    """This will be the main window"""
    data=AOImage()
    
    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,title=title,size=(800,600))
        self.image = CanvasPanel(self) # the canvas for image display
        self.controls = ControlPanel(self) # the control buttons

        
        self.CreateStatusBar() # A Statusbar in the bottom of the window
        
        # Setting up the menu
        filemenu = wx.Menu()
        menuItem_fileopen = filemenu.Append(wx.ID_OPEN,"&0pen"," Open source file")
        filemenu.AppendSeparator()
        menuItem_about = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        filemenu.AppendSeparator()
        menuItem_exit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        
        
        self.Bind(wx.EVT_MENU,self.onOpen,menuItem_fileopen)
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
        self.update_plot()
        
    def update_plot(self):
        self.image.draw(self.data.getCurrent())
        
    def onAbout(self, event):
        """callback for menuitem_about"""
        dlg = wx.MessageDialog( self, "A small app in wxPython", "ConeCounter", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def onExit(self, event):
        """callback for menuitem_exit"""
        self.Close(True)
        
    def onOpen(self, event):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            #f = open(os.path.join(self.dirname, self.filename), 'r')
            #self.control.SetValue(f.read())
            #f.close()
        dlg.Destroy()
        self.loadFrame(os.path.join(self.dirname,self.filename))
        
    def loadFrame(self, fname):
        """Load a frame from a file"""
        if not os.path.isfile(fname):
            logger.error('Invalid filename: %s provided',fname)
            raise IOError
        
        image = mh.imread(fname)
        image = image[:,:,0]
        if image.size == 1:
            #There are problems with some greyscale png images
            logger.error('Invalid image: %s provided: is it grayscale png?',fname)
            raise TypeError,"Invalid image type"       
    
        self.data.setOriginal(image)
        self.update_plot()
        
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)    
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.debug('XXXXXX')
    app = wx.App(False)
    frame = MyFrame(None,'ConeCounter')
    app.MainLoop()