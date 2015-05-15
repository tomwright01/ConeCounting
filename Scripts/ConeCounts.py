import numpy as np
import os
import wx
import logging

import AOImage
import CanvasPanel
import DisplayObjects
                
class MyFrame(wx.Frame):
    """This will be the main window, Subpanels that are children of this frame
    are expected to have a function registerControls that returns a dict
    containing all the important controls with their current state.
    Subpanels with controls that affect the image display should be based on the
    GenericControlPanel class this converts events from the widgets to the
    generic type EVT_STATE_CHANGE, controls registered in self.controls are
    then automatically updated
    
    """
    data=AOImage.AOImage()
    controls = dict() #A dictionary to register controls from all the subpanels
    
    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,title=title,size=(800,600))
        self.image = CanvasPanel.CanvasPanel(self) # the canvas for image display
       
        pnlControls = wx.Panel(self)       
        
        processControls = DisplayObjects.ControlPanel(pnlControls,'ProcessControls') # the control buttons
        displayControls = DisplayObjects.DisplayPanel(pnlControls,'DisplayControls')
        
        logger.debug('registering: %s',displayControls.registerControls())
        logger.debug('registering: %s',processControls.registerControls())        
        
        self.registerControl('DisplayControls',displayControls.registerControls())
        self.registerControl('ProcessControls',processControls.registerControls())
                             
        processControls.Bind(DisplayObjects.GenericControlPanel.EVT_STATE_CHANGE,self.on_control_change)
        displayControls.Bind(DisplayObjects.GenericControlPanel.EVT_STATE_CHANGE,self.on_control_change)
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
        #create an panel to hold the control dialogs
         
        pnlControls_sizer = wx.BoxSizer(wx.VERTICAL)
        pnlControls_sizer.Add(processControls,flag=wx.EXPAND)
        pnlControls_sizer.Add(displayControls,flag=wx.EXPAND)
        pnlControls.SetSizer(pnlControls_sizer)
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.image, proportion=2, flag=wx.EXPAND, border=1)
        self.sizer.Add(pnlControls, proportion=1, flag=wx.EXPAND, border=5)
        
        #Layout sizers
        self.SetSizer(self.sizer)
        #self.SetAutoLayout(1)
        #self.sizer.Fit(self)
        
        self.Show(True)
        self.update_plot()
        
    def on_control_change(self,evt):
        #catches a EVT_STATE_CHANGE and updates the controls dictionary with info from the event
        logger.debug('Event Caught %s',evt.pnlName + '.' + evt.src)
        self.controls[evt.pnlName + '.' + evt.src] = evt.value
        self.update_plot()
        
    def registerControl(self,control,myControls):
        """take the name of a subpanel and a list of controls in that panel
        updates self.controls dictionary"""
        for key in myControls.keys():
            self.controls[control + '.' + key] = myControls[key]
        
    #def on_update_spin(self,event):
        #logger.debug('Caught spin event at main panel, with value %s',event.GetEventObject().getName())
        #srcObj = event.GetEventObject()
        #if srcObj.getName() == 'Filter':
            #self.data.setFilter(srcObj.getValue())
        #else:
            #logger.warning('Unhandled event')
            
        #self.update_plot()
        
    def update_plot(self):
        self.data.setFilter(self.controls['ProcessControls.filter'])
                            
        if self.controls['DisplayControls.cmb_select_base_image'] == 'Current':
            self.image.draw(self.data.getCurrent())
        else:
            self.image.draw(self.data.getOriginal())
        if self.controls['DisplayControls.chkb_show_overlay']:
            self.image.overlayImage(self.data.getMaximaImage())
        
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
        self.data.loadFrame(os.path.join(self.dirname,self.filename))
        self.update_plot()
        
        
if __name__ == '__main__':
    logger = logging.getLogger('ConeCounter')
    formatter = logging.Formatter('%(module)s : %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)    
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.debug('XXXXXX')
    app = wx.App(False)
    frame = MyFrame(None,'ConeCounter')
    app.MainLoop()