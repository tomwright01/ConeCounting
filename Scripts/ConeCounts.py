import numpy as np
import os
import wx
import logging

import AOImage
import CanvasPanel
import DisplayObjects
import FileControl
import AOFileObjects
                

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
        self.FileList = AOFileObjects.AOFileList()
        
        self.image = CanvasPanel.CanvasPanel(self, style = wx.BORDER_RAISED) # the canvas for image display
       
        self.pnlControls = wx.Panel(self,style=wx.BORDER_RAISED)       
        
        processControls = DisplayObjects.ControlPanel(self.pnlControls, name='ProcessControls', style = wx.BORDER_SUNKEN|wx.EXPAND) # the control buttons
        displayControls = DisplayObjects.DisplayPanel(self.pnlControls, name='DisplayControls', style = wx.BORDER_SUNKEN|wx.EXPAND)
        
        self.resultsControls = DisplayObjects.ResultsPanel(self.pnlControls, name='ResultsControls', style = wx.BORDER_SUNKEN|wx.EXPAND) 
        
        self.registerControl('DisplayControls',displayControls.registerControls())
        self.registerControl('ProcessControls',processControls.registerControls())
                             
        processControls.Bind(DisplayObjects.GenericControlPanel.EVT_STATE_CHANGE,self.on_control_change)
        displayControls.Bind(DisplayObjects.GenericControlPanel.EVT_STATE_CHANGE,self.on_control_change)
        
        
        self.image.Bind(CanvasPanel.CanvasPanel.EVT_AXES_CHANGE, self.on_axes_change)
        self.CreateStatusBar() # A Statusbar in the bottom of the window
        
        # Setting up the menu
        self.filemenu = wx.Menu()
        menuItem_fileopen = self.filemenu.Append(wx.ID_OPEN,"&0pen File..."," Open source file")
        menuItem_diropen = self.filemenu.Append(wx.ID_FILE,"Open &Dir...","Open source directory")
        self.filemenu.AppendSeparator()
        menuItem_loadprogress = self.filemenu.Append(wx.ID_FILE1,"&Load Progress..."," Load progress file")
        self.filemenu.AppendSeparator()                                         
        menuItem_save = self.filemenu.Append(wx.ID_SAVE,"&Save Progress...","Save progress file")
        menuItem_save.Enable(False)
        self.filemenu.AppendSeparator()
        menuItem_about = self.filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        self.filemenu.AppendSeparator()
        menuItem_exit = self.filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        
        
        self.Bind(wx.EVT_MENU,self.onOpen,menuItem_fileopen)
        self.Bind(wx.EVT_MENU,self.onOpenDir,menuItem_diropen)
        self.Bind(wx.EVT_MENU,self.onLoadProgress,menuItem_loadprogress)
        self.Bind(wx.EVT_MENU,self.onSaveProgress,menuItem_save)
        self.Bind(wx.EVT_MENU,self.onAbout,menuItem_about)
        self.Bind(wx.EVT_MENU,self.onExit,menuItem_exit)
        
        #Creating the menubar
        menuBar = wx.MenuBar()
        menuBar.Append(self.filemenu,"&File") #adding the filemenu to the menubar
        self.SetMenuBar(menuBar)
        
        #setup the layout
        #create an panel to hold the control dialogs
         
        pnlControls_sizer = wx.BoxSizer(wx.VERTICAL)
        pnlControls_sizer.Add(processControls, flag=wx.EXPAND)
        pnlControls_sizer.Add(displayControls, flag=wx.EXPAND)
        pnlControls_sizer.Add(self.resultsControls, flag=wx.EXPAND)
        
        
        self.pnlControls.SetSizer(pnlControls_sizer)
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.image, proportion=1, flag=wx.EXPAND, border=1)
        self.sizer.Add(self.pnlControls, proportion=0, flag=wx.EXPAND, border=5)
        
        #Layout sizers
        self.SetSizer(self.sizer)
        
        self.Show(True)
        self.update_plot()

    def change_statusbar(self, msg):
        self.SetStatusText(msg)        

    def on_axes_change(self,event):
        logger.debug('Axes change event detected')
        nCones = self.data.GetConeCounts(self.image.GetAxesLimits())
        self.resultsControls.updateConeCounts(nCones)
        
    def on_control_change(self,evt):
        #catches a EVT_STATE_CHANGE and updates the controls dictionary with info from the event
        logger.debug('Event Caught %s',evt.pnlName + '.' + evt.src)
        self.controls[evt.pnlName + '.' + evt.src] = evt.value
        if evt.pnlName in ['ProcessControls','DisplayControls']:
            #only need to update the plot if the display is modified.
            self.update_plot()
        
    def registerControl(self,control,myControls):
        """take the name of a subpanel and a list of controls in that panel
        updates self.controls dictionary"""
        for key in myControls.keys():
            self.controls[control + '.' + key] = myControls[key]
        
       
    def update_plot(self):
        self.data.setFilter(self.controls['ProcessControls.filter'])
        self.data.setMinConeSize(self.controls['ProcessControls.min_cone_size'])
        self.data.setDisplayConeSize(self.controls['DisplayControls.display_cone_size'])

        if self.controls['DisplayControls.cmb_select_base_image'] == 'Current':
            self.image.draw(self.data.getCurrent())
        else:
            self.image.draw(self.data.getOriginal())

        if self.controls['DisplayControls.chkb_show_overlay']:
            self.image.overlayImage(self.data.getMaximaImage())

        nCones = self.data.GetConeCounts(self.image.GetAxesLimits())
        self.resultsControls.updateConeCounts(nCones)
        
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
        filename = None
        dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            #self._loadImage(os.path.join(dirname,filename))
        dlg.Destroy()
        self.FileList = AOFileObjects.AOFileList()
        self._loadImage(os.path.join(dirname,filename))
        self._displayImage()
        
    def onLoadProgress(self, event):
        """Load a progress file and use contents to initialise AOFileList"""
        self.FileList = AOFileObjects.AOFileList()
        self.FileList.Load(self)
        self._addFileControl()
        self._displayImage()
       

    
    def _loadImage(self,fname):
        assert(fname is not None)
        assert(fname != '')
        self.FileList.add(filename = fname)
        
    def _displayImage(self):
        self.data.__init__()
        self.data.loadFrame(self.FileList.GetCurrent().filename)
        self.image.SetAxesLimits(self.data.GetImageSize())
        self.update_plot()
        self.change_statusbar('Images:{0} Unprocessed:{1} Current:{2}'.
                      format(len(self.FileList),
                             len(self.FileList.GetIncomplete()),
                             self.FileList.GetCurrent().filename))        
        
    def _addFileControl(self):
        """add the file control panel"""
        if not 'FileControls' in [x.Name for x in self.pnlControls.Children]:
            #add the control panel
            fileControls = FileControl.FileControl(self.pnlControls,name='FileControls', style = wx.BORDER_SUNKEN)
            self.registerControl('FileControls',fileControls.registerControls())
            fileControls.Bind(DisplayObjects.GenericControlPanel.EVT_STATE_CHANGE,self.on_control_change)
            self.pnlControls.Sizer.Add(fileControls, flag=wx.EXPAND)
            self.pnlControls.Sizer.Layout()
            self.filemenu.FindItemById(wx.ID_SAVE).Enable(True)
            
            #bind the events from the subpanel
            self.Bind(fileControls.EVT_MOVE_NEXT,self._moveNext)
            self.Bind(fileControls.EVT_MARK_COMPLETE,self._markComplete)        
            self.Bind(fileControls.EVT_MARK_SKIP,self._markSkip)  
        
    def onOpenDir(self,event):
        """call back for open dir menu
        creates an AOFileList object to store info on all
        images found in the selected file structure"""
        #create a dialog box to choose the top level directory
        dlg = wx.DirDialog(self, "Choose a directory")
        
        if dlg.ShowModal() == wx.ID_OK:
            self.dirpath = dlg.GetPath()

            self.FileList = AOFileObjects.AOFileList() #add a new filelist to overwrite any that exists
            imgFiles = ['.jpg','.jpeg','.png','.bmp','.tif','.tiff']
            for root, dirs, filenames in os.walk(self.dirpath):
                for filename in filenames:
                    if os.path.splitext(filename)[1].lower() in imgFiles:
                        self.FileList.add(filename = os.path.join(root,filename))
            logger.debug('found %s image files',len(self.FileList))        
            self._addFileControl()

            self._displayImage()
          
        dlg.Destroy()
        
        
    def _moveNext(self,event):
        """Call back function for EVT_MOVE_NEXT,
        loads the next unprocessed image from the FileList"""
        logger.debug("Move next event detected")
        try:
            self.FileList.GetRandomIncomplete()
            self._displayImage()
        except StopIteration:
            self.warn('Finished')

        
    def warn(self,msg,caption = 'Warning'):
        #function to popup a warning message
        dlg = wx.MessageDialog(self,msg,caption,wx.OK|wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy
        
    def _markComplete(self,event):
        """Call back function for EVT_MARK_COMPLETE,
        updates the meta info in FileList"""
        #if self.controls['ProcessControls.filter']
        obj = self.FileList.GetCurrent()
        obj.filtersize = self.controls['ProcessControls.filter']
        obj.conesize = self.controls['ProcessControls.min_cone_size']
        obj.notes = self.controls['FileControls.txt_notes']
        nCones = self.data.GetConeCounts(self.image.GetAxesLimits())
        obj.totalcones = nCones[0]
        obj.regioncones= nCones[1]
        obj.region = self.image.GetAxesLimits()
        obj.complete = True
        logger.debug("Mark complete event detected")   
        self._moveNext(event)
        
    def _markSkip(self,event):
        if self.controls['FileControls.txt_notes'] == '':
            self.warn('You must add a note for an unscored image')
            logger.warning('You must add a note for an unscored image')
        self.FileList.GetCurrent().complete=True
        self.FileList.GetCurrent().notes='SKIPPED' + self.controls['FileControls.txt_notes']
        logger.debug('Unscored image')     
        self._moveNext(event)

    def onSaveProgress(self,event):
        logger.debug('save event fired')
        self.FileList.Save(self)
        
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